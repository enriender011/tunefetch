from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .download import KEEP_ORIGINAL, OUTPUT_FORMATS, download, probe
from .quality import MATCH_THRESHOLD, AudioQuality, combined_score, match_score
from .sources import SEARCH_PREFIXES, Candidate, search

PROBE_PER_SOURCE = 3


@dataclass(frozen=True)
class Ranked:
    candidate: Candidate
    match: float
    quality: AudioQuality | None
    score: float


def is_url(text: str) -> bool:
    return text.startswith(("http://", "https://"))


def collect(query: str, sources: list[str], limit: int) -> list[Candidate]:
    def run(source: str) -> list[Candidate]:
        try:
            return search(source, query, limit)
        except Exception as error:
            print(f"  [{source}] search failed: {error}", file=sys.stderr)
            return []

    with ThreadPoolExecutor() as pool:
        return [item for batch in pool.map(run, sources) for item in batch]


def rank(query: str, candidates: list[Candidate], with_quality: bool) -> list[Ranked]:
    scored = [(c, match_score(query, c.title, c.uploader)) for c in candidates]

    def evaluate(pair: tuple[Candidate, float]) -> Ranked:
        candidate, match = pair
        quality = None
        if with_quality and match >= MATCH_THRESHOLD:
            try:
                quality = probe(candidate.url)
            except Exception:
                quality = None
        return Ranked(candidate, match, quality, combined_score(match, quality))

    with ThreadPoolExecutor() as pool:
        ranked = list(pool.map(evaluate, scored))
    return sorted(ranked, key=lambda item: item.score, reverse=True)


def print_ranked(items: list[Ranked]) -> None:
    for position, item in enumerate(items, start=1):
        quality = item.quality.label() if item.quality else "quality unknown"
        print(f"{position:>2}. [{item.candidate.source}] {item.candidate.title}  ({quality}, match {item.match:.0%})")
        print(f"      {item.candidate.url}")


def command_search(args: argparse.Namespace) -> int:
    candidates = collect(args.query, args.source, args.limit)
    if not candidates:
        print("No results.")
        return 1
    print_ranked(rank(args.query, candidates, with_quality=args.quality)[: args.limit * len(args.source)])
    return 0


def command_get(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)

    if is_url(args.query):
        print(f"Downloading {args.query}")
        download(args.query, output_dir, args.format)
        return 0

    candidates = collect(args.query, args.source, PROBE_PER_SOURCE)
    ranked = rank(args.query, candidates, with_quality=True)
    if not ranked or ranked[0].match < MATCH_THRESHOLD:
        print("No confident match found. Try `tunefetch search` to review the candidates.")
        print_ranked(ranked[:5])
        return 1

    best = ranked[0]
    quality = best.quality.label() if best.quality else "quality unknown"
    print(f"Best: [{best.candidate.source}] {best.candidate.title} ({quality})")
    download(best.candidate.url, output_dir, args.format)
    print(f"Saved in {output_dir.resolve()}")
    return 0


def command_sources(_: argparse.Namespace) -> int:
    for name in SEARCH_PREFIXES:
        print(name)
    print("Any other site supported by yt-dlp (Bandcamp, Internet Archive...) works when you pass its URL to `get`.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tunefetch", description="Search and download music from several sources.")
    parser.add_argument("--version", action="version", version=f"tunefetch {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    def add_source_option(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "-s",
            "--source",
            nargs="+",
            choices=list(SEARCH_PREFIXES),
            default=list(SEARCH_PREFIXES),
            help="Sources to search. Default: all.",
        )

    search_command = commands.add_parser("search", help="List matches without downloading.")
    search_command.add_argument("query")
    search_command.add_argument("-n", "--limit", type=int, default=5, help="Results per source. Default: 5.")
    search_command.add_argument("--quality", action="store_true", help="Also check the audio quality (slower).")
    add_source_option(search_command)
    search_command.set_defaults(handler=command_search)

    get_command = commands.add_parser("get", help="Download a track by name or URL.")
    get_command.add_argument("query", help='"artist - title", or a track/album/playlist URL.')
    get_command.add_argument("-o", "--output", default="downloads", help="Output folder. Default: downloads.")
    get_command.add_argument(
        "-f",
        "--format",
        choices=OUTPUT_FORMATS,
        default=KEEP_ORIGINAL,
        help="Output format. 'best' keeps the original audio without re-encoding. Default: best.",
    )
    add_source_option(get_command)
    get_command.set_defaults(handler=command_get)

    sources_command = commands.add_parser("sources", help="List the available sources.")
    sources_command.set_defaults(handler=command_sources)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
