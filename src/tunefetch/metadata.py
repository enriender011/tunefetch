from __future__ import annotations

import json
import time
from dataclasses import dataclass
from statistics import median
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import __version__
from .quality import tokenize

API_URL = "https://musicbrainz.org/ws/2/recording"
USER_AGENT = f"tunefetch/{__version__}"
RESULT_LIMIT = 25
MIN_SCORE = 80
MIN_QUERY_COVERAGE = 0.8
MIN_PRECISION = 0.6
MIN_ARTIST_COVERAGE = 0.6
RETRY_DELAY = 1.5


@dataclass(frozen=True)
class TrackInfo:
    artist: str
    title: str
    duration: float | None = None

    @property
    def name(self) -> str:
        return f"{self.artist} - {self.title}"


def build_query(text: str) -> str:
    artist, separator, title = text.partition(" - ")
    if separator and artist.strip() and title.strip():

        def quote(value: str) -> str:
            return '"' + value.strip().replace("\\", " ").replace('"', " ") + '"'

        return f"artist:{quote(artist)} AND recording:{quote(title)}"
    return text


def pick_track(data: dict, query: str) -> TrackInfo | None:
    """First recording whose artist and title cover the query and add few unrelated words.

    MusicBrainz free-text search often ranks a different song first, so a wrong identification is worse than none.
    """
    wanted = set(tokenize(query))
    if not wanted:
        return None

    accepted: list[tuple[str, str, float | None]] = []
    for recording in data.get("recordings") or []:
        if int(recording.get("score", 0)) < MIN_SCORE or not recording.get("title"):
            continue
        credits = recording.get("artist-credit") or []
        artist = "".join(f"{item.get('name', '')}{item.get('joinphrase', '')}" for item in credits).strip()
        found = set(tokenize(f"{artist} {recording['title']}"))
        artist_tokens = set(tokenize(artist))
        if not artist_tokens or not found:
            continue

        shared = len(wanted & found)
        if (
            shared / len(wanted) < MIN_QUERY_COVERAGE
            or shared / len(found) < MIN_PRECISION
            or len(wanted & artist_tokens) / len(artist_tokens) < MIN_ARTIST_COVERAGE
        ):
            continue

        length = recording.get("length")
        accepted.append((artist, recording["title"], length / 1000 if length else None))

    if not accepted:
        return None

    artist, title, _ = accepted[0]
    lengths = [length for name, _, length in accepted if name == artist and length]
    return TrackInfo(artist=artist, title=title, duration=median(lengths) if lengths else None)


def lookup(query: str, timeout: float = 8.0) -> TrackInfo | None:
    """Identify a track on MusicBrainz. Returns None when offline or when nothing matches well."""
    params = {"query": build_query(query), "limit": RESULT_LIMIT, "fmt": "json"}
    request = Request(
        f"{API_URL}?{urlencode(params)}", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    for attempt in range(2):
        try:
            with urlopen(request, timeout=timeout) as response:
                return pick_track(json.load(response), query)
        except HTTPError as error:
            if error.code != 503 or attempt == 1:
                return None
            time.sleep(RETRY_DELAY)
        except (URLError, OSError, ValueError):
            return None
    return None
