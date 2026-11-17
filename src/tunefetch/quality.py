from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

LOSSLESS_CODECS = ("flac", "alac", "wav", "pcm", "aiff", "ape", "wavpack")
UNWANTED_WORDS = frozenset({"cover", "karaoke", "live", "remix", "instrumental", "reaction", "tutorial", "slowed"})
MATCH_THRESHOLD = 0.6
LOSSLESS_SCORE = 1000.0


@dataclass(frozen=True)
class AudioQuality:
    codec: str
    abr: float | None = None

    @property
    def lossless(self) -> bool:
        return self.codec.lower().startswith(LOSSLESS_CODECS)

    @property
    def score(self) -> float:
        return LOSSLESS_SCORE if self.lossless else (self.abr or 0.0)

    def label(self) -> str:
        if self.lossless:
            return f"{self.codec} (lossless)"
        return f"{self.codec} {self.abr:.0f}k" if self.abr else self.codec


def tokenize(text: str) -> list[str]:
    folded = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+", ascii_text)


def match_score(query: str, title: str, uploader: str | None = None) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0

    candidate_tokens = set(tokenize(f"{title} {uploader or ''}"))
    score = len(query_tokens & candidate_tokens) / len(query_tokens)
    score -= 0.15 * len((candidate_tokens & UNWANTED_WORDS) - query_tokens)
    return max(0.0, min(1.0, score))


def combined_score(match: float, quality: AudioQuality | None) -> float:
    if match < MATCH_THRESHOLD:
        return match * 50
    quality_part = min(quality.score if quality else 0.0, LOSSLESS_SCORE) / 10
    return match * 100 + quality_part
