"""Tests for live-test production refusal and env gating."""

from __future__ import annotations

import pytest

from posiverse.config import PROD_BASE_URL, PosiverseConfig
from tests.live_guard import LiveTestGuard


def test_live_guard_refuses_production():
    """Live markers must not contact the production OpenAPI host."""
    with pytest.raises(RuntimeError, match="refuse the production"):
        LiveTestGuard.assert_not_production(PROD_BASE_URL)
    with pytest.raises(RuntimeError, match="refuse the production"):
        LiveTestGuard.assert_not_production(PROD_BASE_URL + "/")


def test_live_guard_rejects_http():
    """Live tests require https even for non-prod hosts."""
    with pytest.raises(ValueError, match="https"):
        LiveTestGuard.assert_not_production("http://internal.example.invalid")


def test_live_guard_accepts_https_override():
    """A non-prod https override is accepted."""
    url = LiveTestGuard.assert_not_production("https://internal.example.invalid/")
    assert url == "https://internal.example.invalid"


def test_live_guard_requires_env(monkeypatch):
    """POSIVERSE_BASE_URL is required for live tests."""
    monkeypatch.delenv(PosiverseConfig.BASE_URL_ENV, raising=False)
    with pytest.raises(pytest.skip.Exception, match="POSIVERSE_BASE_URL"):
        LiveTestGuard.require_base_url()


def test_live_guard_require_uses_env(monkeypatch):
    """When the env var is set to a non-prod https URL, live tests use it."""
    monkeypatch.setenv(PosiverseConfig.BASE_URL_ENV, "https://internal.example.invalid")
    assert LiveTestGuard.require_base_url() == "https://internal.example.invalid"


def test_live_guard_require_refuses_prod_env(monkeypatch):
    """Setting POSIVERSE_BASE_URL to production still fails closed."""
    monkeypatch.setenv(PosiverseConfig.BASE_URL_ENV, PROD_BASE_URL)
    with pytest.raises(RuntimeError, match="refuse the production"):
        LiveTestGuard.require_base_url()
