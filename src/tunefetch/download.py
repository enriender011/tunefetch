from __future__ import annotations

import re
import shutil
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.postprocessor.metadataparser import MetadataParserPP

from .metadata import TrackInfo
from .quality import AudioQuality

KEEP_ORIGINAL = "best"
DEFAULT_FORMAT = "mp3"
OUTPUT_FORMATS = ("mp3", "m4a", "opus", "flac", "wav", KEEP_ORIGINAL)
# Conversion quality chosen to add as little extra loss as possible: mp3 VBR 0 (about 245 kbps), AAC 256 kbps.
CONVERSION_QUALITY = {"mp3": "0", "m4a": "256"}
COVER_FORMATS = ("mp3", "m4a", "opus", "flac")
TRACK_NAME = "%(artist,uploader|Unknown)s - %(title)s"
EXTENSION = "%(ext)s"


def missing_tools() -> list[str]:
    """ffmpeg converts the audio and writes the tags; ffprobe is needed to read the files."""
    return [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]


def _base_options() -> dict:
    return {"quiet": True, "no_warnings": True, "format": "bestaudio/best"}


def probe(url: str) -> AudioQuality | None:
    with yt_dlp.YoutubeDL({**_base_options(), "noplaylist": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    return best_audio_quality((info or {}).get("formats") or [])


def best_audio_quality(formats: list[dict]) -> AudioQuality | None:
    best: AudioQuality | None = None
    for fmt in formats:
        codec = fmt.get("acodec")
        if not codec or codec == "none" or fmt.get("vcodec") not in (None, "none"):
            continue
        quality = AudioQuality(codec=codec, abr=fmt.get("abr") or fmt.get("tbr"))
        if best is None or quality.score > best.score:
            best = quality
    return best


def safe_filename(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text).strip(" .") or "track"


def _literal(text: str) -> str:
    return text.replace("%", "%%")


def metadata_actions(track: TrackInfo) -> list:
    """yt-dlp metadata actions that set artist and title.

    yt-dlp reads a single-word source (such as an artist called "Estopa") as a field name and stores NA. The trailing
    space makes it a literal, and the same space in the target pattern keeps it out of the stored value.
    """
    return [
        (MetadataParserPP.interpretter, f"{_literal(track.artist)} ", "%(artist)s "),
        (MetadataParserPP.interpretter, f"{_literal(track.title)} ", "%(title)s "),
    ]


def is_youtube_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com")


def split_title_actions() -> list:
    """Turn a "Artist - Song" video title into separate artist and title fields.

    Without it the file would be named after the channel plus the full title: "Estopa - Estopa - Vino Tinto".
    The artist part is matched lazily so "Artist - Song - Live" keeps "Song - Live" as the title.
    Only for YouTube: on SoundCloud or Bandcamp the uploader is the artist and a dash in the title is part of the
    song name ("Light Pace - Free - CC0").
    """
    return [(MetadataParserPP.interpretter, "title", r"(?P<artist>.+?) - (?P<title>.+)")]


def collection_folder(info: dict | None) -> str | None:
    """Folder name for an album or playlist with several tracks. A single track, or a list of one, gets none."""
    if not info or info.get("_type") != "playlist":
        return None
    entries = [entry for entry in (info.get("entries") or []) if entry]
    title = info.get("title") or info.get("id")
    if len(entries) < 2 or not title:
        return None
    return safe_filename(str(title))


def output_template(track: TrackInfo | None = None, folder: str | None = None) -> str:
    if track:
        return f"{_literal(safe_filename(track.name))}.{EXTENSION}"
    if folder:
        return f"{_literal(folder)}/%(playlist_index)02d - {TRACK_NAME}.{EXTENSION}"
    return f"{TRACK_NAME}.{EXTENSION}"


def find_collection_folder(url: str) -> str | None:
    options = {**_base_options(), "skip_download": True, "extract_flat": "in_playlist"}
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            return collection_folder(ydl.extract_info(url, download=False, process=False))
    except Exception:
        return None


def download(
    url: str,
    output_dir: Path,
    output_format: str = DEFAULT_FORMAT,
    on_progress: Callable[[dict], None] | None = None,
    track: TrackInfo | None = None,
    detect_collection: bool = False,
) -> None:
    folder = find_collection_folder(url) if detect_collection and track is None else None
    template = output_template(track, folder)
    options = {
        **_base_options(),
        "noprogress": True,
        "allow_playlist_files": False,
        "outtmpl": str(output_dir / template),
        "windowsfilenames": True,
        "postprocessors": [{"key": "FFmpegMetadata"}],
    }

    actions = metadata_actions(track) if track else split_title_actions() if is_youtube_url(url) else []
    if actions:
        options["postprocessors"].insert(0, {"key": "MetadataParser", "when": "pre_process", "actions": actions})

    if output_format in COVER_FORMATS:
        options["writethumbnail"] = True
        options["postprocessors"].append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
    if output_format != KEEP_ORIGINAL:
        extract = {"key": "FFmpegExtractAudio", "preferredcodec": output_format}
        if output_format in CONVERSION_QUALITY:
            extract["preferredquality"] = CONVERSION_QUALITY[output_format]
        options["postprocessors"].insert(0, extract)
    if on_progress:
        options["progress_hooks"] = [on_progress]

    output_dir.mkdir(parents=True, exist_ok=True)
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
