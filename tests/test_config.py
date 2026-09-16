"""Tests for PosiverseConfig static helpers."""

from __future__ import annotations

import pytest

from posiverse.config import DEFAULT_BASE_URL, PROD_BASE_URL, PosiverseConfig


def test_resolve_defaults_to_production(monkeypatch):
    """With no argument and no env var, production is used."""
    monkeypatch.delenv(PosiverseConfig.BASE_URL_ENV, raising=False)
    assert PosiverseConfig.resolve_base_url() == PROD_BASE_URL == DEFAULT_BASE_URL


def test_resolve_strips_trailing_slash():
    """Trailing slashes are normalized away."""
    url = PosiverseConfig.resolve_base_url("https://example.invalid/")
    assert url == "https://example.invalid"


def test_resolve_rejects_http():
    """HTTP is not an allowed scheme."""
    with pytest.raises(ValueError, match="https"):
        PosiverseConfig.resolve_base_url("http://example.invalid")


def test_resolve_rejects_empty():
    """Whitespace-only explicit URLs fall through, empty strings after strip fail via env/default."""
    with pytest.raises(ValueError, match="host"):
        PosiverseConfig.normalize_base_url("https://")


def test_is_production_host():
    """Production host detection ignores path and trailing slash."""
    assert PosiverseConfig.is_production_host(PROD_BASE_URL) is True
    assert PosiverseConfig.is_production_host(PROD_BASE_URL + "/") is True
    assert PosiverseConfig.is_production_host("https://example.invalid") is False


def test_redact_text_and_secret():
    """Redaction never returns the original secret."""
    secret = "abc-secret-value"
    assert PosiverseConfig.redact_secret(secret) == "***"
    assert secret not in PosiverseConfig.redact_text(f"key={secret}", secret)
    assert PosiverseConfig.redact_text("plain", None) == "plain"


def test_coerce_timeout_rejects_none():
    """Timeouts cannot be disabled."""
    with pytest.raises(ValueError, match="timeout"):
        PosiverseConfig.coerce_timeout(None)
    assert PosiverseConfig.coerce_timeout(5.0) == 5.0
