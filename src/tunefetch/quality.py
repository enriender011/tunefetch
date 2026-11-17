from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

LOSSLESS_CODECS = ("flac", "alac", "wav", "pcm", "aiff", "ape", "wavpack")
UNWANTED_WORDS = frozenset({"cover", "karaoke", "live", "remix", "instrumental", "reaction", "tutorial", "slowed"})
MATCH_THRESHOLD = 0.6
MATCH_TOLERANCE = 0.1
LOSSLESS_SCORE = 1000.0
PREVIEW_SECONDS = 45.0
DURATION_TOLERANCE = 6.0
DURATION_PENALTY_FROM = 15.0
DURATION_PENALTY = 0.3

# Rough perceived-quality weight of a lossy codec compared with mp3 at the same bitrate.
CODEC_EFFICIENCY = (("opus", 1.35), ("mp4a", 1.15), ("aac", 1.15), ("vorbis", 1.1))


@dataclass(frozen=True)
class AudioQuality:
    codec: str
    abr: float | None = None

    @property
    def lossless(self) -> bool:
        return self.codec.lower().startswith(LOSSLESS_CODECS)

    @property
    def score(self) -> float:
        if self.lossless:
            return LOSSLESS_SCORE
        codec = self.codec.lower()
        factor = next((weight for prefix, weight in CODEC_EFFICIENCY if codec.startswith(prefix)), 1.0)
        return (self.abr or 0.0) * factor

    def label(self, lossless_word: str = "lossless") -> str:
        if self.lossless:
            return f"{self.codec} ({lossless_word})"
        return f"{self.codec} {self.abr:.0f}k" if self.abr else self.codec


def tokenize(text: str) -> list[str]:
    folded = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+", ascii_text)


def _overlap(reference: str, candidate_tokens: set[str]) -> float:
    reference_tokens = set(tokenize(reference))
    if not reference_tokens:
        return 0.0
    return len(reference_tokens & candidate_tokens) / len(reference_tokens)


def match_score(query: str, title: str, uploader: str | None = None, identified: str | None = None) -> float:
    """Share of the query (or of the identified "artist title") found in the candidate, minus unwanted words."""
    candidate_tokens = set(tokenize(f"{title} {uploader or ''}"))
    wanted = set(tokenize(query)) | set(tokenize(identified or ""))
    score = max(_overlap(query, candidate_tokens), _overlap(identified or "", candidate_tokens))
    score -= 0.15 * len((candidate_tokens & UNWANTED_WORDS) - wanted)
    return max(0.0, min(1.0, score))


def duration_adjusted(match: float, expected: float | None, actual: float | None) -> float:
    if not actual:
        return match

    is_preview = actual < PREVIEW_SECONDS and not (expected and expected < PREVIEW_SECONDS)
    differs = bool(expected) and abs(expected - actual) > DURATION_PENALTY_FROM
    return max(0.0, match - DURATION_PENALTY) if is_preview or differs else match


def rank_key(match: float, quality: AudioQuality | None, best_match: float) -> tuple[int, float, float]:
    """Sort key, higher first.

    Quality only orders the matches that are about as good as the best one. A remix or a different song never
    outranks the real track because it has a higher bitrate.
    """
    if match < MATCH_THRESHOLD:
        return (0, 0.0, match)
    if match < best_match - MATCH_TOLERANCE:
        return (1, 0.0, match)
    return (2, quality.score if quality else 0.0, match)


def duration_matches(expected: float | None, actual: float | None) -> bool:
    return bool(expected and actual and abs(expected - actual) <= DURATION_TOLERANCE)
