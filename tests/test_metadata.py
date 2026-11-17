from urllib.error import HTTPError, URLError

import yt_dlp
from yt_dlp.postprocessor.metadataparser import MetadataParserPP

from tunefetch import metadata
import pytest

from tunefetch.download import best_audio_quality, is_youtube_url, metadata_actions, safe_filename, split_title_actions
from tunefetch.metadata import TrackInfo, build_query, pick_track


def recording(title: str, artist: str, length: int | None = 200_000, score: int = 100) -> dict:
    return {"score": score, "title": title, "length": length, "artist-credit": [{"name": artist}]}


def test_build_query_splits_artist_and_title():
    assert build_query("Queen - Bohemian Rhapsody") == 'artist:"Queen" AND recording:"Bohemian Rhapsody"'
    assert build_query("Queen Bohemian Rhapsody") == "Queen Bohemian Rhapsody"


def test_pick_track_accepts_a_good_match_and_uses_the_median_length():
    data = {
        "recordings": [
            recording("Vino tinto", "Estopa", None),
            recording("Vino tinto", "Estopa", 196_000),
            recording("Vino tinto", "Estopa", 198_000),
            recording("Vino tinto", "Estopa", 260_000),
        ]
    }
    track = pick_track(data, "Estopa - Vino tinto")
    assert track is not None
    assert (track.artist, track.title, track.duration) == ("Estopa", "Vino tinto", 198.0)


def test_pick_track_rejects_a_different_artist():
    data = {"recordings": [recording("Queen - Bohemian Rhapsody", "Kyle Landry", 317_000)]}
    assert pick_track(data, "Queen Bohemian Rhapsody") is None


def test_pick_track_rejects_titles_that_add_many_unrelated_words():
    data = {"recordings": [recording("The Queen's Bohemian Rhapsody", "And Be Done With It", 355_000)]}
    assert pick_track(data, "Queen Bohemian Rhapsody") is None


def test_pick_track_ignores_low_scores_and_empty_data():
    assert pick_track({"recordings": [recording("Vino tinto", "Estopa", score=40)]}, "Estopa - Vino tinto") is None
    assert pick_track({}, "Estopa - Vino tinto") is None


def test_pick_track_skips_a_bad_first_result_and_takes_the_next_good_one():
    data = {"recordings": [recording("Other song", "Estopa"), recording("Vino tinto", "Estopa", 198_000)]}
    track = pick_track(data, "Estopa - Vino tinto")
    assert track is not None and track.title == "Vino tinto"


def test_lookup_retries_once_on_503_and_then_gives_up(monkeypatch):
    calls = []

    def always_503(request, timeout):
        calls.append(request)
        raise HTTPError(request.full_url, 503, "Service Temporarily Unavailable", {}, None)

    monkeypatch.setattr(metadata, "urlopen", always_503)
    monkeypatch.setattr(metadata, "RETRY_DELAY", 0)
    assert metadata.lookup("Estopa - Vino tinto") is None
    assert len(calls) == 2


def test_lookup_does_not_retry_other_errors(monkeypatch):
    calls = []

    def offline(request, timeout):
        calls.append(request)
        raise URLError("offline")

    monkeypatch.setattr(metadata, "urlopen", offline)
    assert metadata.lookup("Estopa - Vino tinto") is None
    assert len(calls) == 1


def test_metadata_actions_set_artist_and_title_even_for_single_words():
    for track in (TrackInfo("Estopa", "Vino tinto"), TrackInfo("Queen", "Bohemian Rhapsody"), TrackInfo("AC/DC", "100%")):
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            processor = MetadataParserPP(ydl, metadata_actions(track))
            info = {"title": "video title", "uploader": "someone"}
            processor.run(info)
        assert (info["artist"], info["title"]) == (track.artist, track.title)


def parse_title(title: str, uploader: str = "Some Channel") -> dict:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = {"title": title, "uploader": uploader}
        MetadataParserPP(ydl, split_title_actions()).run(info)
    return info


def test_an_artist_dash_song_title_is_split_into_two_fields():
    info = parse_title("Estopa - Vino Tinto", "Estopa")
    assert (info["artist"], info["title"]) == ("Estopa", "Vino Tinto")


def test_only_the_first_dash_splits_the_title():
    info = parse_title("Estopa - Vino Tinto - Live 2020")
    assert (info["artist"], info["title"]) == ("Estopa", "Vino Tinto - Live 2020")


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=abc", True),
        ("https://music.youtube.com/watch?v=abc", True),
        ("https://youtu.be/abc", True),
        ("https://soundcloud.com/artist/track", False),
        ("https://artist.bandcamp.com/album/name", False),
        ("https://notyoutube.com/watch?v=abc", False),
        ("https://youtube.com.evil.example/x", False),
    ],
)
def test_the_title_is_only_split_for_youtube_links(url, expected):
    assert is_youtube_url(url) is expected


def test_a_title_without_a_dash_is_left_alone():
    info = parse_title("Vino Tinto (Estopa)")
    assert "artist" not in info and info["title"] == "Vino Tinto (Estopa)"


def test_safe_filename_removes_path_characters():
    assert safe_filename("AC/DC - Who Made Who?") == "AC_DC - Who Made Who_"
    assert safe_filename("...") == "track"


def test_best_audio_quality_ignores_video_formats_and_picks_the_highest():
    formats = [
        {"acodec": "mp4a.40.2", "vcodec": "avc1", "abr": 192},
        {"acodec": "opus", "vcodec": "none", "abr": 131},
        {"acodec": "mp3", "vcodec": "none", "abr": 128},
        {"acodec": "none", "vcodec": "avc1"},
    ]
    best = best_audio_quality(formats)
    assert best is not None and best.codec == "opus"
    assert best_audio_quality([]) is None
