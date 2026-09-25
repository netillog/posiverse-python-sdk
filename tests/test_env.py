"""Tests for project-root .env loading (no python-dotenv)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from posiverse._env import find_dotenv, load_dotenv


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _unset(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    """Remove env names for this test and restore prior values afterward."""
    for name in names:
        # setenv records the previous value (or absence) for teardown.
        monkeypatch.setenv(name, "__posiverse_test_sentinel__")
        os.environ.pop(name, None)


def test_load_dotenv_parses_export_quotes_and_comments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """KEY=VALUE lines support export, quotes, and comments without override."""
    env_file = tmp_path / ".env"
    _write(
        env_file,
        "\n".join(
            [
                "# comment",
                "",
                "export POSIVERSE_API_KEY=\"from-file\"",
                "PLAIN=plain-value",
                "SINGLE='quoted'",
                "EMPTY=",
                "NOEQUALS",
                "export =missing-key",
                "=novalue",
            ]
        )
        + "\n",
    )
    _unset(monkeypatch, "POSIVERSE_API_KEY", "PLAIN", "SINGLE", "EMPTY")

    loaded = load_dotenv(env_file)
    assert loaded == env_file
    assert os.environ["POSIVERSE_API_KEY"] == "from-file"
    assert os.environ["PLAIN"] == "plain-value"
    assert os.environ["SINGLE"] == "quoted"
    assert os.environ["EMPTY"] == ""


def test_load_dotenv_does_not_override_existing_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Shell/CI values win when override is left at the default False."""
    env_file = tmp_path / ".env"
    _write(env_file, "POSIVERSE_API_KEY=from-file\nOTHER=from-file\n")
    monkeypatch.setenv("POSIVERSE_API_KEY", "from-shell")
    _unset(monkeypatch, "OTHER")

    load_dotenv(env_file)
    assert os.environ["POSIVERSE_API_KEY"] == "from-shell"
    assert os.environ["OTHER"] == "from-file"


def test_load_dotenv_override_replaces_existing_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """override=True replaces keys already present in os.environ."""
    env_file = tmp_path / ".env"
    _write(env_file, "POSIVERSE_API_KEY=from-file\n")
    monkeypatch.setenv("POSIVERSE_API_KEY", "from-shell")

    load_dotenv(env_file, override=True)
    assert os.environ["POSIVERSE_API_KEY"] == "from-file"


def test_load_dotenv_strips_utf8_bom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A leading UTF-8 BOM (common in Windows Notepad) does not prefix the key."""
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"\xef\xbb\xbfPOSIVERSE_API_KEY=from-bom\n")
    _unset(monkeypatch, "POSIVERSE_API_KEY")

    load_dotenv(env_file)
    assert os.environ["POSIVERSE_API_KEY"] == "from-bom"
    assert "\ufeffPOSIVERSE_API_KEY" not in os.environ


def test_find_dotenv_walks_to_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Search starts at cwd and stops at the directory that holds pyproject.toml."""
    project = tmp_path / "proj"
    nested = project / "sub"
    nested.mkdir(parents=True)
    _write(project / "pyproject.toml", "[project]\nname = 'tmp'\n")
    _write(project / ".env", "POSIVERSE_API_KEY=from-root\n")
    _write(project / ".env.example", "POSIVERSE_API_KEY=\n")
    monkeypatch.chdir(nested)

    found = find_dotenv()
    assert found == (project / ".env").resolve()


def test_find_dotenv_missing_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """No file yields None and does not invent values."""
    project = tmp_path / "empty"
    project.mkdir()
    _write(project / "pyproject.toml", "[project]\nname = 'empty'\n")
    monkeypatch.chdir(project)
    assert find_dotenv() is None
    assert load_dotenv() is None


def test_default_load_does_not_reload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A second default load does not overwrite keys removed after the first load."""
    import posiverse._env as env_module

    project = tmp_path / "proj"
    project.mkdir()
    _write(project / "pyproject.toml", "[project]\nname = 'tmp'\n")
    _write(project / ".env", "POSIVERSE_DOTENV_SENTINEL=first\n")
    monkeypatch.chdir(project)
    monkeypatch.setattr(env_module, "_LOADED", False)
    _unset(monkeypatch, "POSIVERSE_DOTENV_SENTINEL")

    first = load_dotenv()
    assert first == (project / ".env").resolve()
    assert os.environ["POSIVERSE_DOTENV_SENTINEL"] == "first"
    os.environ.pop("POSIVERSE_DOTENV_SENTINEL", None)

    second = load_dotenv()
    assert second == first
    assert "POSIVERSE_DOTENV_SENTINEL" not in os.environ
