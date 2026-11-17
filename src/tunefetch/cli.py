from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from . import __version__
from .config import (
    AUTO,
    config_path,
    default_output,
    load_settings,
    normalize_language,
    normalize_output,
    resolve_language,
    resolve_output,
    save_settings,
)
from .download import DEFAULT_FORMAT, OUTPUT_FORMATS, download, missing_tools, probe
from .errors import translate_parse_error
from .help import render_help
from .i18n import LANGUAGES, set_language, t
from .metadata import TrackInfo, lookup
from .progress import ProgressBar, format_duration
from .quality import MATCH_THRESHOLD, AudioQuality, duration_adjusted, match_score, rank_key
from .sources import SEARCHERS, Candidate, search

PROBE_PER_SOURCE = 3
SETTINGS = ("language", "output")


@dataclass(frozen=True)
class Ranked:
    candidate: Candidate
    match: float
    quality: AudioQuality | None


def is_url(text: str) -> bool:
    return text.startswith(("http://", "https://"))


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def status(message: str) -> None:
    if is_interactive():
        print(f"  {message}", file=sys.stderr, flush=True)


def describe_quality(quality: AudioQuality | None) -> str:
    return quality.label(t("result.lossless")) if quality else t("result.quality_unknown")


def identify(query: str, enabled: bool) -> TrackInfo | None:
    if not enabled:
        return None

    status(t("run.identifying"))
    track = lookup(query)
    if track:
        length = f" ({format_duration(track.duration)})" if track.duration else ""
        print(t("run.identified", name=track.name, length=length))
    else:
        status(t("run.not_identified"))
    return track


def collect(query: str, sources: list[str], limit: int) -> list[Candidate]:
    def run(source: str) -> list[Candidate]:
        try:
            return search(source, query, limit)
        except Exception as error:
            print(f"  {t('run.search_failed', source=source, error=error)}", file=sys.stderr)
            return []

    status(t("run.searching"))
    with ThreadPoolExecutor() as pool:
        return [item for batch in pool.map(run, sources) for item in batch]


def rank(
    query: str, candidates: list[Candidate], with_quality: bool, identified: TrackInfo | None = None
) -> list[Ranked]:
    def evaluate(candidate: Candidate) -> Ranked:
        match = match_score(query, candidate.title, candidate.uploader, identified.name if identified else None)
        match = duration_adjusted(match, identified.duration if identified else None, candidate.duration)
        quality = None
        if with_quality and match >= MATCH_THRESHOLD:
            try:
                quality = probe(candidate.url)
            except Exception:
                quality = None
        return Ranked(candidate, match, quality)

    if with_quality:
        status(t("run.checking_quality"))
    with ThreadPoolExecutor() as pool:
        ranked = list(pool.map(evaluate, candidates))
    best_match = max((item.match for item in ranked), default=0.0)
    return sorted(ranked, key=lambda item: rank_key(item.match, item.quality, best_match), reverse=True)


def print_ranked(items: list[Ranked]) -> None:
    for position, item in enumerate(items, start=1):
        details = [describe_quality(item.quality)]
        if item.candidate.duration:
            details.append(format_duration(item.candidate.duration))
        details.append(t("result.match", percent=f"{item.match:.0%}"))
        print(f"{position:>2}. [{item.candidate.source}] {item.candidate.title}  ({', '.join(details)})")
        print(f"      {item.candidate.url}")


def parse_selection(text: str, count: int) -> list[int]:
    answer = text.strip().lower()
    if not answer:
        return [0]
    if answer in ("q", "quit", "exit"):
        return []

    picks: list[int] = []
    for part in answer.replace(" ", ",").split(","):
        if not part:
            continue
        if not part.isdigit() or not 1 <= int(part) <= count:
            raise ValueError(t("menu.invalid", part=part, count=count))
        index = int(part) - 1
        if index not in picks:
            picks.append(index)
    return picks


def choose(count: int, ranked: list[Ranked], ask: Callable[[str], str] = input) -> list[Ranked]:
    prompt = t("menu.prompt", count=count)
    while True:
        try:
            return [ranked[index] for index in parse_selection(ask(prompt), count)]
        except ValueError as error:
            print(error)
        except EOFError:
            return []


def command_search(args: argparse.Namespace) -> int:
    identified = identify(args.query, not args.no_lookup)
    candidates = collect(args.query, args.source, args.limit)
    if not candidates:
        print(t("run.no_results"))
        return 1
    print_ranked(rank(args.query, candidates, with_quality=args.quality, identified=identified))
    return 0


def command_get(args: argparse.Namespace) -> int:
    missing = missing_tools()
    if missing:
        print(t("run.ffmpeg_missing", tools=", ".join(missing)), file=sys.stderr)
        return 1

    output_dir, _ = resolve_output(args.output)

    if is_url(args.query):
        print(t("run.downloading_link", url=args.query))
        bar = ProgressBar()
        download(args.query, output_dir, args.format, on_progress=bar.hook, detect_collection=True)
        bar.finish()
        print(t("run.saved_in", path=output_dir))
        return 0

    identified = identify(args.query, not args.no_lookup)
    candidates = collect(args.query, args.source, args.limit)
    ranked = rank(args.query, candidates, with_quality=True, identified=identified)
    if not ranked:
        print(t("run.no_results"))
        return 1

    if args.auto or not is_interactive():
        if ranked[0].match < MATCH_THRESHOLD:
            print(t("run.no_confident"))
            print_ranked(ranked[:5])
            return 1
        chosen = ranked[:1]
    else:
        print_ranked(ranked)
        chosen = choose(len(ranked), ranked)
        if not chosen:
            print(t("run.cancelled"))
            return 0

    failures = 0
    for item in chosen:
        print(
            t(
                "run.downloading",
                source=item.candidate.source,
                title=item.candidate.title,
                quality=describe_quality(item.quality),
            )
        )
        track = identified if item.match >= MATCH_THRESHOLD else None
        bar = ProgressBar()
        try:
            download(item.candidate.url, output_dir, args.format, on_progress=bar.hook, track=track)
        except Exception as error:
            failures += 1
            print(f"  {t('run.failed', error=error)}", file=sys.stderr)
        finally:
            bar.finish()

    print(t("run.saved_in", path=output_dir))
    return 1 if failures else 0


def command_sources(_: argparse.Namespace) -> int:
    for name in SEARCHERS:
        print(name)
    print(t("sources.more"))
    return 0


def show_language(flag: str | None) -> None:
    code, origin = resolve_language(flag)
    print(t("config.language", name=LANGUAGES[code], code=code, origin=t(f"origin.{origin}")))


def show_output() -> None:
    path, origin = resolve_output()
    print(t("config.output", path=path, origin=t(f"origin.{origin}")))


def set_language_setting(settings: dict, value: str, flag: str | None) -> int:
    if value.lower() == AUTO:
        settings.pop("language", None)
        save_settings(settings)
        set_language(resolve_language(flag)[0])
        print(t("config.reset"))
        return 0

    code = normalize_language(value)
    if code is None:
        print(
            t("config.bad_language", value=value, options=", ".join([*LANGUAGES, AUTO])),
            file=sys.stderr,
        )
        return 1

    settings["language"] = code
    save_settings(settings)
    set_language(code)
    print(t("config.set", name=LANGUAGES[code]))
    return 0


def set_output_setting(settings: dict, value: str) -> int:
    if value.lower() == AUTO:
        settings.pop("output", None)
        save_settings(settings)
        print(t("config.output_reset", path=default_output()))
        return 0

    path = normalize_output(value)
    if path.is_file():
        print(t("config.output_is_file", path=path), file=sys.stderr)
        return 1

    settings["output"] = str(path)
    save_settings(settings)
    print(t("config.output_set", path=path))
    return 0


def command_config(args: argparse.Namespace) -> int:
    if args.setting is None:
        show_language(args.language_flag)
        show_output()
        print(t("config.file", path=config_path()))
        return 0

    setting = args.setting.lower()
    if setting not in SETTINGS:
        print(t("config.bad_setting", setting=args.setting, options=", ".join(SETTINGS)), file=sys.stderr)
        return 1

    if args.value is None:
        show_language(args.language_flag) if setting == "language" else show_output()
        return 0

    settings = load_settings()
    if setting == "language":
        return set_language_setting(settings, args.value.strip(), args.language_flag)
    return set_output_setting(settings, args.value.strip())


class TunefetchParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        missing_key = {"tunefetch get": "run.missing_get", "tunefetch search": "run.missing_search"}.get(self.prog)
        if missing_key and "arguments are required" in message:
            message = t(missing_key)
        else:
            message = translate_parse_error(message)
        print(t("run.parse_error", message=message), file=sys.stderr)
        raise SystemExit(2)


class HelpAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, command=None, **kwargs):
        super().__init__(option_strings, dest=dest, default=default, nargs=0, **kwargs)
        self.command = command

    def __call__(self, parser, namespace, values, option_string=None):
        print(render_help(self.command))
        raise SystemExit(0)


class VersionAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, **kwargs):
        super().__init__(option_strings, dest=dest, default=default, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(f"tunefetch {__version__}")
        raise SystemExit(0)


def build_parser() -> argparse.ArgumentParser:
    parser = TunefetchParser(prog="tunefetch", add_help=False)
    parser.add_argument("-h", "--help", action=HelpAction, command=None)
    parser.add_argument("--version", action=VersionAction)
    commands = parser.add_subparsers(dest="command", parser_class=TunefetchParser)

    def add_command(name: str, handler: Callable[[argparse.Namespace], int]) -> argparse.ArgumentParser:
        command = commands.add_parser(name, add_help=False)
        command.add_argument("-h", "--help", action=HelpAction, command=name)
        command.set_defaults(handler=handler)
        return command

    def add_search_options(command: argparse.ArgumentParser) -> None:
        command.add_argument("-s", "--source", nargs="+", choices=list(SEARCHERS), default=list(SEARCHERS))
        command.add_argument("-n", "--limit", type=int, default=PROBE_PER_SOURCE)
        command.add_argument("--no-lookup", action="store_true")

    search_command = add_command("search", command_search)
    search_command.add_argument("query")
    search_command.add_argument("--quality", action="store_true")
    add_search_options(search_command)

    get_command = add_command("get", command_get)
    get_command.add_argument("query")
    get_command.add_argument("-o", "--output")
    get_command.add_argument("-f", "--format", choices=OUTPUT_FORMATS, default=DEFAULT_FORMAT)
    get_command.add_argument("--auto", action="store_true")
    add_search_options(get_command)

    add_command("sources", command_sources)

    config_command = add_command("config", command_config)
    config_command.add_argument("setting", nargs="?")
    config_command.add_argument("value", nargs="?")
    return parser


def split_language_option(argv: list[str]) -> tuple[str | None, list[str]]:
    """Take `--lang <code>` out of the arguments so it works before or after the command."""
    pre_parser = TunefetchParser(add_help=False)
    pre_parser.add_argument("--lang", choices=list(LANGUAGES))
    known, rest = pre_parser.parse_known_args(argv)
    return known.lang, rest


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    set_language(resolve_language()[0])
    language_flag, arguments = split_language_option(arguments)
    set_language(resolve_language(language_flag)[0])

    args = build_parser().parse_args(arguments)
    args.language_flag = language_flag
    if args.command is None:
        print(render_help(None))
        return 0

    try:
        return args.handler(args)
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        print(t("run.error", error=error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
