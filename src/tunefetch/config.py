from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from .i18n import DEFAULT_LANGUAGE, LANGUAGES

AUTO = "auto"


def config_dir() -> Path:
    override = os.environ.get("TUNEFETCH_CONFIG_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / "tunefetch"
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "tunefetch"


def config_path() -> Path:
    return config_dir() / "config.json"


def load_settings() -> dict:
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_language(value: str | None) -> str | None:
    """'es', 'es-ES', 'es_ES.UTF-8' and 'Spanish_Spain' all give 'es'. Returns None for unsupported languages."""
    if not value:
        return None
    text = value.strip().lower().replace("_", "-")
    if text.startswith("spanish"):
        return "es"
    if text.startswith("english"):
        return "en"
    code = text.split("-")[0].split(".")[0]
    return code if code in LANGUAGES else None


def system_language() -> str | None:
    if sys.platform == "win32":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer)):
                return normalize_language(buffer.value)
        except (AttributeError, OSError):
            pass

    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        language = normalize_language(os.environ.get(name))
        if language:
            return language
    return None


def resolve_language(flag: str | None = None) -> tuple[str, str]:
    """Return (language code, origin). Order: --lang, TUNEFETCH_LANG, settings file, system, English."""
    candidates = (
        ("flag", flag),
        ("env", os.environ.get("TUNEFETCH_LANG")),
        ("config", load_settings().get("language")),
        ("system", system_language()),
    )
    for origin, value in candidates:
        language = normalize_language(value) if value and value != AUTO else None
        if language:
            return language, origin
    return DEFAULT_LANGUAGE, "default"


def is_writable(folder: Path) -> bool:
    try:
        with tempfile.TemporaryFile(dir=folder):
            return True
    except OSError:
        return False


def default_output() -> Path:
    """The folder of the program when it runs as a standalone .exe, otherwise the folder it was run from.

    With `uv run` or `uv tool install` the executable is a hidden launcher, so the working directory is the useful
    place. If that folder cannot be written to (Program Files, System32), the home folder is used so a download
    never fails for that reason.
    """
    base = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path.cwd()
    return base if is_writable(base) else Path.home()


def normalize_output(text: str) -> Path:
    return Path(text.strip().strip('"')).expanduser().absolute()


def resolve_output(flag: str | None = None) -> tuple[Path, str]:
    """Return (download folder, origin). Order: -o, the settings file, then default_output()."""
    if flag:
        return normalize_output(flag), "flag"
    saved = load_settings().get("output")
    if isinstance(saved, str) and saved.strip():
        return normalize_output(saved), "config"
    return default_output(), "default"
