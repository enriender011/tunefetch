import pytest

from tunefetch.cli import build_parser, choose, is_url, parse_selection
from tunefetch.quality import (
    AudioQuality,
    duration_adjusted,
    duration_matches,
    match_score,
    rank_key,
    tokenize,
)


def test_tokenize_strips_accents_and_punctuation():
    assert tokenize("Qué necesario es el rock&roll") == ["que", "necesario", "es", "el", "rock", "roll"]


def test_lossless_beats_any_lossy_bitrate():
    assert AudioQuality("flac").score > AudioQuality("mp3", 320).score
    assert AudioQuality("flac").lossless
    assert not AudioQuality("opus", 160).lossless


def test_match_score_full_and_partial():
    assert match_score("fito que necesario es el rock", "Fito - Qué necesario es el rock & roll") == 1.0
    assert match_score("fito rock", "Marea - En tu agujero") == 0.0


def test_unwanted_words_lower_the_match_unless_requested():
    plain = match_score("song artist", "Song - Artist")
    cover = match_score("song artist", "Song - Artist (cover)")
    wanted = match_score("song artist cover", "Song - Artist (cover)")
    assert cover < plain
    assert wanted == 1.0


def test_opus_outranks_mp3_at_a_similar_bitrate():
    assert AudioQuality("opus", 131).score > AudioQuality("mp3", 128).score
    assert AudioQuality("mp4a.40.2", 129).score > AudioQuality("mp3", 128).score


def test_equally_good_matches_sort_by_quality_then_match():
    best = 1.0
    results = [
        ("low", rank_key(0.95, AudioQuality("mp3", 128), best)),
        ("lossless", rank_key(0.92, AudioQuality("flac"), best)),
        ("good", rank_key(0.95, AudioQuality("opus", 160), best)),
        ("same-quality-better-match", rank_key(1.0, AudioQuality("opus", 160), best)),
    ]
    ordered = [name for name, key in sorted(results, key=lambda item: item[1], reverse=True)]
    assert ordered == ["lossless", "same-quality-better-match", "good", "low"]


def test_worse_match_never_outranks_the_real_track_on_quality():
    real = rank_key(1.0, AudioQuality("opus", 127), 1.0)
    remix = rank_key(0.85, AudioQuality("mp4a.40.2", 160), 1.0)
    weak = rank_key(0.3, AudioQuality("flac"), 1.0)
    assert real > remix > weak


def test_match_uses_the_identified_name_when_it_fits_better():
    assert match_score("despis", "Despistaos - Es importante") == 0.0
    assert match_score("despis", "Despistaos - Es importante", identified="Despistaos Es importante") == 1.0


def test_duration_far_from_expected_lowers_the_match():
    assert duration_adjusted(0.9, 200, 205) == 0.9
    assert duration_adjusted(0.9, 200, 330) < 0.9
    assert duration_adjusted(0.9, None, 330) == 0.9
    assert duration_adjusted(0.9, 200, None) == 0.9


def test_short_previews_are_penalized_unless_the_track_is_short():
    assert duration_adjusted(1.0, None, 30) < 1.0
    assert duration_adjusted(1.0, 200, 30) < 1.0
    assert duration_adjusted(1.0, 30, 30) == 1.0


def test_duration_matches_within_tolerance():
    assert duration_matches(200, 204)
    assert not duration_matches(200, 230)
    assert not duration_matches(None, 200)


def test_is_url():
    assert is_url("https://example.com/a")
    assert not is_url("artist - title")


def test_parse_selection():
    assert parse_selection("", 5) == [0]
    assert parse_selection("2", 5) == [1]
    assert parse_selection("1, 3 3", 5) == [0, 2]
    assert parse_selection("q", 5) == []
    for bad in ("0", "6", "abc", "1,x"):
        with pytest.raises(ValueError):
            parse_selection(bad, 5)


def test_choose_asks_again_after_invalid_input():
    answers = iter(["9", "2"])
    ranked = ["first", "second", "third"]
    assert choose(3, ranked, ask=lambda _: next(answers)) == ["second"]


def test_choose_cancels_on_end_of_input():
    def closed(_: str) -> str:
        raise EOFError

    assert choose(3, ["a", "b", "c"], ask=closed) == []


def test_cli_defaults():
    args = build_parser().parse_args(["get", "artist - title"])
    assert args.format == "mp3"
    assert args.output is None
    assert args.source == ["youtube", "soundcloud"]
