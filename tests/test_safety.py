"""Safety tests: unit tests never target production; library omits the test host."""

from __future__ import annotations

from pathlib import Path

from posiverse import DEFAULT_BASE_URL, PROD_BASE_URL, PosiverseClient
from posiverse.config import PosiverseConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
PROD_HOST = "openapi-prod.posiverse.com"
TEST_HOST = "openapi-test.posiverse.com"


def test_default_url_is_production():
    """The SDK default must be the production server documented in OpenAPI."""
    assert DEFAULT_BASE_URL == PROD_BASE_URL == PosiverseConfig.PRODUCTION_BASE_URL
    assert PROD_BASE_URL == "https://openapi-prod.posiverse.com"
    assert not hasattr(PosiverseClient, "TEST_BASE_URL")


def test_test_base_url_is_not_exported():
    """Published package must not ship a TEST_BASE_URL helper."""
    import posiverse

    assert not hasattr(posiverse, "TEST_BASE_URL")
    assert "TEST_BASE_URL" not in posiverse.__all__


def test_live_smoke_does_not_hardcode_hosts():
    """Live smoke must require POSIVERSE_BASE_URL and refuse production."""
    live = (REPO_ROOT / "tests" / "test_live_smoke.py").read_text(encoding="utf-8")
    assert PROD_HOST not in live
    assert TEST_HOST not in live
    assert "POSIVERSE_BASE_URL" in live


def test_ci_workflow_does_not_call_prod_or_enable_live():
    """CI must run mocked tests plus audit (no live/prod configuration)."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert PROD_HOST not in ci
    assert "POSIVERSE_LIVE_SMOKE" not in ci
    assert "POSIVERSE_LIVE_INTEGRATION" not in ci
    assert "pip-audit" in ci
    assert "ruff" in ci
    assert "pytest" in ci
