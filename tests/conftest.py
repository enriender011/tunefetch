import pytest

from tunefetch import i18n


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Keep the tests away from the real settings file, language variables and the current language."""
    monkeypatch.setenv("TUNEFETCH_CONFIG_DIR", str(tmp_path / "config"))
    for name in ("TUNEFETCH_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("tunefetch.config.system_language", lambda: None)
    monkeypatch.setattr("tunefetch.cli.missing_tools", lambda: [])
    i18n.set_language("en")
    yield
    i18n.set_language("en")
