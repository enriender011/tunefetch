from __future__ import annotations

import re
import sys
from pathlib import Path

from . import __version__
from .i18n import t

COMMANDS = ("get", "search", "sources", "config")

# "tunefetch" followed by a command or an argument placeholder, never preceded by a path character.
COMMAND_PATTERN = re.compile(r"(?<![\w./\\-])tunefetch (?=(?:get|search|sources|config|<))")

PLACEHOLDERS = ("song", "link", "folder", "format", "name", "number", "setting", "value")

# Left columns use {name} markers that are replaced with the translated placeholder (ph.<name> messages).
SOURCE_OPTION = ("-s, --source <{name}...>", "opt.source")
LIMIT_OPTION = ("-n, --limit <{number}>", "opt.limit")
LOOKUP_OPTION = ("--no-lookup", "opt.no_lookup")

ARGUMENTS = {
    "get": [("<{song}|{link}>", "arg.get.query")],
    "search": [("<{song}>", "arg.search.query")],
    "config": [("[{setting}]", "arg.config.setting"), ("[{value}]", "arg.config.value")],
}

OPTIONS = {
    "get": [
        ("-o, --output <{folder}>", "opt.output"),
        ("-f, --format <{format}>", "opt.format"),
        ("--auto", "opt.auto"),
        SOURCE_OPTION,
        LIMIT_OPTION,
        LOOKUP_OPTION,
    ],
    "search": [("--quality", "opt.quality"), SOURCE_OPTION, LIMIT_OPTION, LOOKUP_OPTION],
}

SETTINGS = {"config": [("language", "set.language"), ("output", "set.output")]}

ENVIRONMENT = [
    ("TUNEFETCH_LANG", "env.lang"),
    ("TUNEFETCH_CONFIG_DIR", "env.config_dir"),
]

GENERAL_OPTIONS = [
    ("--lang <en|es>", "opt.lang"),
    ("--version", "opt.version"),
    ("-h, --help", "opt.help"),
]

EXAMPLES = {
    None: [
        ('tunefetch get "Estopa - Vino tinto"', "ex.main.get"),
        ('tunefetch get "Estopa - Vino tinto" --auto', "ex.main.auto"),
        ('tunefetch get "Estopa - Vino tinto" -f m4a', "ex.main.m4a"),
        ('tunefetch get "Estopa - Vino tinto" -o D:\\Music', "ex.main.output"),
        ("tunefetch get https://soundcloud.com/artist/sets/album", "ex.main.link"),
        ("tunefetch config output D:\\Music", "ex.main.config_output"),
        ("tunefetch config language es", "ex.main.lang"),
    ],
    "get": [
        ('tunefetch get "Estopa - Vino tinto"', "ex.get.menu"),
        ('tunefetch get "Estopa - Vino tinto" --auto', "ex.get.auto"),
        ('tunefetch get "Estopa - Vino tinto" -f m4a', "ex.get.format"),
        ('tunefetch get "Estopa - Vino tinto" -o D:\\Music', "ex.get.output"),
        ("tunefetch get https://soundcloud.com/artist/sets/album", "ex.get.album"),
    ],
    "search": [
        ('tunefetch search "Estopa - Vino tinto"', "ex.search.basic"),
        ('tunefetch search "Estopa - Vino tinto" --quality', "ex.search.quality"),
    ],
    "sources": [("tunefetch sources", "ex.sources.list")],
    "config": [
        ("tunefetch config", "ex.config.show"),
        ("tunefetch config language es", "ex.config.set"),
        ("tunefetch config language auto", "ex.config.auto"),
        ("tunefetch config output D:\\Music", "ex.config.output"),
        ("tunefetch config output auto", "ex.config.output_auto"),
    ],
}

MAIN_COMMAND_SUMMARIES = {name: f"cmd.{name}" for name in COMMANDS}


def _table(rows: list[tuple[str, str]], indent: int = 2) -> list[str]:
    width = max(len(left) for left, _ in rows)
    return [f"{' ' * indent}{left.ljust(width)}  {right}" for left, right in rows]


def _translated(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    words = {name: t(f"ph.{name}") for name in PLACEHOLDERS}
    return [(left.format(**words), t(key)) for left, key in rows]


def render_help(command: str | None = None) -> str:
    lines = [f"tunefetch {__version__}", t("help.tagline"), ""]
    lines += [f"{t('help.usage')}:", f"  {t('usage.main' if command is None else f'usage.{command}')}", ""]

    if command is None:
        lines += [f"{t('help.commands')}:"]
        lines += _table([(name, t(MAIN_COMMAND_SUMMARIES[name])) for name in COMMANDS])
        lines += [""]
        for name in ("get", "search"):
            lines += [f"{t(f'help.{name}_options')}:"] + _table(_translated(OPTIONS[name])) + [""]
    else:
        lines += [t(f"desc.{command}"), ""]
        if command in ARGUMENTS:
            lines += [f"{t('help.arguments')}:"] + _table(_translated(ARGUMENTS[command])) + [""]
        if command in OPTIONS:
            lines += [f"{t('help.options')}:"] + _table(_translated(OPTIONS[command])) + [""]
        if command in SETTINGS:
            lines += [f"{t('help.settings')}:"] + _table(_translated(SETTINGS[command])) + [""]

    if EXAMPLES.get(command):
        lines += [f"{t('help.examples')}:"] + _table(_translated(EXAMPLES[command])) + [""]
    lines += [f"{t('help.general')}:"] + _table(_translated(GENERAL_OPTIONS)) + [""]
    if command is None:
        lines += [f"{t('help.environment')}:"] + _table(_translated(ENVIRONMENT)) + [""]
        lines += [t("help.footer"), ""]
    return _with_program_name("\n".join(lines))


def program_name() -> str:
    """How the user starts the program: `.\\tunefetch.exe` for the standalone Windows file, `tunefetch` otherwise."""
    if getattr(sys, "frozen", False):
        name = Path(sys.executable).name
        return f".\\{name}" if sys.platform == "win32" else f"./{name}"
    return "tunefetch"


def _with_program_name(text: str) -> str:
    """Write commands in the help the way they are typed. The version line and plain prose are left alone."""
    program = program_name()
    if program == "tunefetch":
        return text
    return COMMAND_PATTERN.sub(lambda _: f"{program} ", text)
