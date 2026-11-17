import sys
from pathlib import Path

import pytest

from tunefetch import cli, config
from tunefetch.download import collection_folder, output_template
from tunefetch.i18n import set_language
from tunefetch.metadata import TrackInfo


def playlist(title: str | None, entries: int, kind: str = "playlist") -> dict:
    return {"_type": kind, "title": title, "id": "abc", "entries": [{"id": str(n)} for n in range(entries)]}


def test_a_single_track_gets_no_folder():
    assert collection_folder({"_type": "video", "title": "Song"}) is None
    assert collection_folder(None) is None


def test_a_list_with_one_track_gets_no_folder():
    assert collection_folder(playlist("My list", 1)) is None
    assert collection_folder(playlist("My list", 0)) is None


def test_an_album_with_several_tracks_gets_a_folder_named_after_it():
    assert collection_folder(playlist("Mi Álbum", 2)) == "Mi Álbum"


def test_folder_name_is_safe_for_the_file_system():
    assert collection_folder(playlist('AC/DC: "Back in Black"?', 5)) == "AC_DC_ _Back in Black__"


def test_entries_that_are_none_do_not_count():
    assert collection_folder({"_type": "playlist", "title": "X", "entries": [{"id": "1"}, None]}) is None


def test_templates_for_a_single_track_an_album_and_an_identified_track():
    assert output_template() == "%(artist,uploader|Unknown)s - %(title)s.%(ext)s"
    assert output_template(folder="Album").startswith("Album/%(playlist_index)02d - ")
    assert output_template(track=TrackInfo("Estopa", "Vino tinto")) == "Estopa - Vino tinto.%(ext)s"
    assert output_template(folder="100%").startswith("100%%/")


def test_default_folder_without_an_exe_is_the_folder_the_command_runs_from(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr(sys, "frozen", raising=False)
    folder, origin = config.resolve_output()
    assert folder.resolve() == tmp_path.resolve() and origin == "default"
    assert config.default_output().resolve() == tmp_path.resolve()


def test_default_folder_of_a_standalone_exe_is_the_folder_of_the_exe(tmp_path, monkeypatch):
    app = tmp_path / "app"
    app.mkdir()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(app / "tunefetch.exe"))
    monkeypatch.chdir(tmp_path)
    assert config.default_output() == app.resolve()


def test_default_folder_falls_back_to_home_when_it_cannot_be_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(config, "is_writable", lambda folder: False)
    assert config.default_output() == Path.home()


def test_is_writable(tmp_path):
    assert config.is_writable(tmp_path)
    assert not config.is_writable(tmp_path / "does-not-exist")


def test_download_folder_priority_flag_then_settings_then_home(tmp_path):
    config.save_settings({"output": str(tmp_path / "saved")})
    assert config.resolve_output() == (tmp_path / "saved", "config")
    assert config.resolve_output(str(tmp_path / "flag")) == (tmp_path / "flag", "flag")


def test_relative_and_home_paths_become_absolute():
    assert config.normalize_output("music").is_absolute()
    assert config.normalize_output("~/music") == Path.home() / "music"
    assert config.normalize_output('  "music"  ').name == "music"


def test_config_output_can_be_set_shown_and_reset(tmp_path, capsys):
    folder = tmp_path / "my music"
    assert cli.main(["config", "output", str(folder)]) == 0
    assert config.load_settings() == {"output": str(folder)}
    capsys.readouterr()

    assert cli.main(["config", "output"]) == 0
    assert str(folder) in capsys.readouterr().out

    assert cli.main(["config"]) == 0
    output = capsys.readouterr().out
    assert str(folder) in output and "Language:" in output

    assert cli.main(["config", "output", "auto"]) == 0
    assert config.load_settings() == {}
    assert str(config.default_output()) in capsys.readouterr().out


def test_config_output_rejects_a_file(tmp_path, capsys):
    file = tmp_path / "file.txt"
    file.write_text("x")
    assert cli.main(["config", "output", str(file)]) == 1
    assert "is a file" in capsys.readouterr().err
    assert config.load_settings() == {}


def test_setting_one_option_keeps_the_other(tmp_path):
    cli.main(["config", "language", "es"])
    cli.main(["config", "output", str(tmp_path / "m")])
    assert config.load_settings() == {"language": "es", "output": str(tmp_path / "m")}


def test_get_uses_the_configured_folder_and_a_flag_overrides_it(tmp_path, monkeypatch):
    saved, flag = tmp_path / "saved", tmp_path / "flag"
    calls = []
    monkeypatch.setattr(cli, "download", lambda url, folder, *args, **kwargs: calls.append((folder, kwargs)))
    config.save_settings({"output": str(saved)})

    assert cli.main(["get", "https://example.com/album"]) == 0
    assert cli.main(["get", "https://example.com/album", "-o", str(flag)]) == 0

    assert [folder for folder, _ in calls] == [saved, flag]
    assert all(kwargs["detect_collection"] for _, kwargs in calls)


def test_main_help_lists_every_option_of_get_and_search():
    for language in ("en", "es"):
        set_language(language)
        from tunefetch.help import render_help

        text = render_help(None)
        for flag in ("--output", "--format", "--auto", "--source", "--limit", "--no-lookup", "--quality"):
            assert flag in text, f"{flag} missing from the {language} main help"


@pytest.mark.parametrize("language", ["en", "es"])
def test_config_help_lists_both_settings(language):
    from tunefetch.help import render_help

    set_language(language)
    text = render_help("config")
    assert "language" in text and "output" in text
