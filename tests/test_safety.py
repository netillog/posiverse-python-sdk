"""Safety tests: unit tests never target the production OpenAPI host."""

from __future__ import annotations

from pathlib import Path

from posiverse import DEFAULT_BASE_URL, PROD_BASE_URL, TEST_BASE_URL

REPO_ROOT = Path(__file__).resolve().parents[1]
PROD_HOST = "openapi-prod.posiverse.com"


def test_default_url_is_test_not_prod():
    """The SDK default must be the test server documented in OpenAPI servers[]."""
    assert DEFAULT_BASE_URL == TEST_BASE_URL
    assert TEST_BASE_URL == "https://openapi-test.posiverse.com"
    assert PROD_BASE_URL == "https://openapi-prod.posiverse.com"
    assert DEFAULT_BASE_URL != PROD_BASE_URL


def test_live_smoke_file_only_mentions_test_host():
    """The optional live smoke test must not contain the production host."""
    live = (REPO_ROOT / "tests" / "test_live_smoke.py").read_text(encoding="utf-8")
    assert PROD_HOST not in live
    assert "openapi-test.posiverse.com" in live


def test_ci_workflow_does_not_call_prod():
    """CI must run mocked tests only (no live/prod configuration)."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert PROD_HOST not in ci
    assert "POSIVERSE_LIVE_SMOKE" not in ci
