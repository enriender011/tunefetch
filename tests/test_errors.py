import pytest

from tunefetch import cli, download
from tunefetch.errors import translate_parse_error
from tunefetch.i18n import set_language


def run(capsys, *arguments: str) -> str:
    with pytest.raises(SystemExit) as stopped:
        cli.main(list(arguments))
    assert stopped.value.code == 2
    return capsys.readouterr().err


@pytest.mark.parametrize(
    ("arguments", "english", "spanish"),
    [
        (
            ("get", "x", "-f", "mp5"),
            "'mp5' is not valid for -f/--format. Choose from: mp3, m4a",
            "'mp5' no es válido para -f/--format. Elige entre: mp3, m4a",
        ),
        (("get", "x", "-s", "tidal"), "Choose from: youtube, soundcloud", "Elige entre: youtube, soundcloud"),
        (
            ("get", "x", "-n", "abc"),
            "-n/--limit needs a whole number, not 'abc'",
            "-n/--limit necesita un número entero, no 'abc'",
        ),
        (("get", "x", "-o"), "-o/--output needs a value", "-o/--output necesita un valor"),
        (("get", "x", "-s"), "-s/--source needs a value", "-s/--source necesita un valor"),
        (
            ("get", "x", "--nope"),
            "Unknown option or extra argument: --nope",
            "Opción desconocida o argumento sobrante: --nope",
        ),
        (
            ("frobnicate",),
            "Unknown command 'frobnicate'. Available: search, get, sources, config",
            "Comando desconocido 'frobnicate'. Disponibles: search, get, sources, config",
        ),
    ],
)
def test_parse_errors_are_translated(capsys, arguments, english, spanish):
    assert english in run(capsys, "--lang", "en", *arguments)
    assert spanish in run(capsys, "--lang", "es", *arguments)


def test_an_invalid_language_is_reported_in_the_language_from_the_settings(capsys):
    cli.main(["config", "language", "es"])
    capsys.readouterr()
    error = run(capsys, "--lang", "fr", "get", "x")
    assert "'fr' no es válido para --lang" in error


def test_unknown_messages_are_left_as_they_are():
    set_language("es")
    assert translate_parse_error("something new from argparse") == "something new from argparse"


def test_get_stops_with_install_instructions_when_ffmpeg_is_missing(monkeypatch, capsys):
    monkeypatch.setattr(cli, "missing_tools", lambda: ["ffmpeg", "ffprobe"])
    searched = []
    monkeypatch.setattr(cli, "collect", lambda *args: searched.append(args) or [])

    assert cli.main(["--lang", "en", "get", "Estopa - Vino tinto"]) == 1
    error = capsys.readouterr().err
    assert "Missing ffmpeg, ffprobe" in error and "winget install Gyan.FFmpeg" in error
    assert searched == []

    assert cli.main(["--lang", "es", "get", "https://example.com/a"]) == 1
    assert "Falta ffmpeg, ffprobe" in capsys.readouterr().err


def test_search_does_not_need_ffmpeg(monkeypatch):
    monkeypatch.setattr(cli, "missing_tools", lambda: ["ffmpeg", "ffprobe"])
    monkeypatch.setattr(cli, "collect", lambda *args: [])
    assert cli.main(["search", "x", "--no-lookup"]) == 1


def test_missing_tools_reports_what_is_not_installed(monkeypatch):
    monkeypatch.setattr(download.shutil, "which", lambda name: None if name == "ffprobe" else f"/bin/{name}")
    assert download.missing_tools() == ["ffprobe"]
    monkeypatch.setattr(download.shutil, "which", lambda name: f"/bin/{name}")
    assert download.missing_tools() == []
