from tunefetch.cli import build_parser, is_url
from tunefetch.quality import AudioQuality, combined_score, match_score, tokenize


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


def test_combined_score_prefers_better_quality_on_equal_match():
    good = combined_score(1.0, AudioQuality("flac"))
    lossy = combined_score(1.0, AudioQuality("mp3", 128))
    assert good > lossy


def test_poor_match_never_wins_on_quality_alone():
    right = combined_score(1.0, AudioQuality("opus", 128))
    wrong = combined_score(0.3, AudioQuality("flac"))
    assert right > wrong


def test_is_url():
    assert is_url("https://example.com/a")
    assert not is_url("artist - title")


def test_cli_defaults():
    args = build_parser().parse_args(["get", "artist - title"])
    assert args.format == "best"
    assert args.output == "downloads"
    assert args.source == ["youtube", "soundcloud"]
