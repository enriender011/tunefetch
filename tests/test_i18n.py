import string
import sys

import pytest

from tunefetch import cli, config, i18n
from tunefetch import help as help_module
from tunefetch.help import COMMANDS, render_help
from tunefetch.i18n import MESSAGES, set_language, t


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_every_language_has_exactly_the_same_messages():
    english = set(MESSAGES["en"])
    for code, messages in MESSAGES.items():
        assert set(messages) == english, f"{code} is out of sync: {set(messages) ^ english}"


def test_every_message_uses_the_same_placeholders_in_all_languages():
    for key, text in MESSAGES["en"].items():
        for code, messages in MESSAGES.items():
            assert placeholders(messages[key]) == placeholders(text), f"{key} in {code}"


def test_language_names_cover_every_catalog():
    assert set(i18n.LANGUAGES) == set(MESSAGES)


def test_unknown_language_falls_back_to_english():
    set_language("fr")
    assert i18n.get_language() == "en"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("es", "es"), ("es-ES", "es"), ("es_ES.UTF-8", "es"), ("Spanish_Spain", "es"), ("en-US", "en"), ("fr", None), ("", None)],
)
def test_normalize_language(value, expected):
    assert config.normalize_language(value) == expected


def test_language_priority_flag_then_env_then_settings_then_system(monkeypatch):
    assert config.resolve_language() == ("en", "default")

    monkeypatch.setattr(config, "system_language", lambda: "es")
    assert config.resolve_language() == ("es", "system")

    config.save_settings({"language": "en"})
    assert config.resolve_language() == ("en", "config")

    monkeypatch.setenv("TUNEFETCH_LANG", "es")
    assert config.resolve_language() == ("es", "env")
    assert config.resolve_language("en") == ("en", "flag")


def test_corrupt_settings_file_is_ignored():
    config.config_path().parent.mkdir(parents=True)
    config.config_path().write_text("{not json", encoding="utf-8")
    assert config.load_settings() == {}


def test_config_command_sets_and_resets_the_language(capsys):
    assert cli.main(["config", "language", "es"]) == 0
    assert "Español" in capsys.readouterr().out
    assert config.load_settings() == {"language": "es"}

    assert cli.main(["config"]) == 0
    output = capsys.readouterr().out
    assert "Idioma: Español (es)" in output
    assert "config.json" in output

    assert cli.main(["config", "language", "auto"]) == 0
    assert config.load_settings() == {}


def test_config_command_rejects_unknown_values(capsys):
    assert cli.main(["config", "language", "klingon"]) == 1
    assert "klingon" in capsys.readouterr().err
    assert cli.main(["config", "color", "red"]) == 1
    assert "color" in capsys.readouterr().err
    assert config.load_settings() == {}


def test_lang_flag_works_before_and_after_the_command(capsys):
    assert cli.main(["--lang", "es", "sources"]) == 0
    assert "Cualquier otro sitio" in capsys.readouterr().out
    assert cli.main(["sources", "--lang", "en"]) == 0
    assert "Any other site" in capsys.readouterr().out


def test_running_without_a_command_shows_the_main_help(capsys):
    assert cli.main([]) == 0
    assert "get" in capsys.readouterr().out


@pytest.mark.parametrize("language", list(MESSAGES))
@pytest.mark.parametrize("command", [None, *COMMANDS])
def test_help_lists_every_option_of_the_command(language, command):
    set_language(language)
    text = render_help(command)
    parser = cli.build_parser()
    target = parser
    if command:
        target = parser._subparsers._group_actions[0].choices[command]  # noqa: SLF001
    flags = {flag for action in target._actions for flag in action.option_strings}  # noqa: SLF001
    for flag in flags:
        assert flag in text, f"{flag} is missing from the {language} help of {command}"
    assert "--lang" in text and "--help" in text


def test_help_flag_prints_the_translated_help(capsys):
    with pytest.raises(SystemExit) as stopped:
        cli.main(["--lang", "es", "get", "--help"])
    assert stopped.value.code == 0
    output = capsys.readouterr().out
    assert "Uso:" in output and "Ejemplos:" in output and "Opciones:" in output


def test_missing_arguments_get_a_friendly_message_in_the_selected_language(capsys):
    for command, expected in (("get", "Falta la canción o el enlace"), ("search", "Falta la canción.")):
        with pytest.raises(SystemExit) as stopped:
            cli.main(["--lang", "es", command])
        assert stopped.value.code == 2
        error = capsys.readouterr().err
        assert expected in error and "Ejecuta `tunefetch --help`" in error


def test_help_placeholders_are_translated():
    set_language("es")
    text = render_help("get")
    assert "<canción|enlace>" in text and "<carpeta>" in text
    assert "<song" not in text and "<folder>" not in text


def test_selection_error_is_translated():
    set_language("es")
    with pytest.raises(ValueError, match="no es un número"):
        cli.parse_selection("9", 3)


@pytest.mark.parametrize("language", list(MESSAGES))
def test_main_help_lists_the_environment_variables(language):
    set_language(language)
    text = render_help(None)
    assert "TUNEFETCH_LANG" in text and "TUNEFETCH_CONFIG_DIR" in text


@pytest.fixture
def windows_exe(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "executable", str(tmp_path / "tunefetch.exe"))


@pytest.mark.parametrize("command", [None, *COMMANDS])
def test_a_standalone_windows_exe_shows_the_commands_as_they_are_typed(windows_exe, command):
    text = render_help(command)
    typed = ".\\tunefetch.exe"
    assert text.splitlines()[0].startswith("tunefetch ")
    assert f"  {typed} " in text
    assert "  tunefetch get" not in text and "  tunefetch config" not in text and "  tunefetch search" not in text
    assert f"`{typed} " in render_help(None) or command is not None


def test_the_exe_name_follows_the_file_name_the_user_gave_it(monkeypatch, tmp_path, windows_exe):
    monkeypatch.setattr(sys, "executable", str(tmp_path / "music.exe"))
    assert ".\\music.exe get" in render_help("get")


def test_prose_that_names_the_program_is_not_rewritten(windows_exe):
    assert "where tunefetch can search" in render_help("sources")


def test_a_standalone_exe_outside_windows_uses_dot_slash(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(sys, "executable", str(tmp_path / "tunefetch"))
    assert help_module.program_name() == "./tunefetch"


def test_running_from_source_keeps_the_plain_name(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert help_module.program_name() == "tunefetch"
    assert '  tunefetch get "Estopa - Vino tinto"' in render_help(None)
