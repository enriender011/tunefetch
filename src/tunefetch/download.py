from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import yt_dlp

from .quality import AudioQuality

KEEP_ORIGINAL = "best"
OUTPUT_FORMATS = (KEEP_ORIGINAL, "mp3", "m4a", "opus", "flac", "wav")
COVER_FORMATS = ("mp3", "m4a", "opus", "flac")
OUTPUT_TEMPLATE = "%(playlist_title&{}/|)s%(artist,uploader|Unknown)s - %(title)s.%(ext)s"


def _base_options() -> dict:
    return {"quiet": True, "no_warnings": True, "format": "bestaudio/best"}


def probe(url: str) -> AudioQuality | None:
    with yt_dlp.YoutubeDL({**_base_options(), "noplaylist": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    best: AudioQuality | None = None
    for fmt in (info or {}).get("formats") or []:
        codec = fmt.get("acodec")
        if not codec or codec == "none" or fmt.get("vcodec") not in (None, "none"):
            continue
        quality = AudioQuality(codec=codec, abr=fmt.get("abr") or fmt.get("tbr"))
        if best is None or quality.score > best.score:
            best = quality
    return best


def download(
    url: str,
    output_dir: Path,
    output_format: str = KEEP_ORIGINAL,
    on_progress: Callable[[dict], None] | None = None,
) -> None:
    options = {
        **_base_options(),
        "noprogress": True,
        "outtmpl": str(output_dir / OUTPUT_TEMPLATE),
        "windowsfilenames": True,
        "postprocessors": [{"key": "FFmpegMetadata"}],
    }

    if output_format in COVER_FORMATS:
        options["writethumbnail"] = True
        options["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
    if output_format != KEEP_ORIGINAL:
        options["postprocessors"].insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": output_format})
    if on_progress:
        options["progress_hooks"] = [on_progress]

    output_dir.mkdir(parents=True, exist_ok=True)
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
