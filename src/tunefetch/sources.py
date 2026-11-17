from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import yt_dlp


@dataclass(frozen=True)
class Candidate:
    source: str
    title: str
    url: str
    uploader: str | None = None
    duration: float | None = None


def _ytdlp_search(source: str, prefix: str) -> Callable[[str, int], list[Candidate]]:
    def run(query: str, limit: int) -> list[Candidate]:
        options = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(f"{prefix}{limit}:{query}", download=False)

        candidates: list[Candidate] = []
        for entry in (info or {}).get("entries") or []:
            url = entry.get("webpage_url") or entry.get("url")
            title = entry.get("title")
            if not url or not title:
                continue
            candidates.append(
                Candidate(
                    source=source,
                    title=title,
                    url=url,
                    uploader=entry.get("uploader") or entry.get("channel"),
                    duration=entry.get("duration"),
                )
            )
        return candidates

    return run


SEARCHERS: dict[str, Callable[[str, int], list[Candidate]]] = {
    "youtube": _ytdlp_search("youtube", "ytsearch"),
    "soundcloud": _ytdlp_search("soundcloud", "scsearch"),
}


def search(source: str, query: str, limit: int = 5) -> list[Candidate]:
    return SEARCHERS[source](query, limit)
