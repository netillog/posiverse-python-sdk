"""Env-gated live test helpers.

Live tests never default to production. They require ``POSIVERSE_BASE_URL``
(an internal test OpenAPI base URL) and refuse the production host.
"""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse

import pytest

from posiverse.config import PosiverseConfig


class LiveTestGuard:
    """Static helpers that gate live tests away from production."""

    BASE_URL_ENV = PosiverseConfig.BASE_URL_ENV
    API_KEY_ENV = PosiverseConfig.API_KEY_ENV
    LIVE_SMOKE_ENV = "POSIVERSE_LIVE_SMOKE"
    LIVE_INTEGRATION_ENV = "POSIVERSE_LIVE_INTEGRATION"
    FORBIDDEN_PROD_HOST = "openapi-prod.posiverse.com"

    @staticmethod
    def smoke_or_integration_enabled() -> bool:
        """Return True when either live smoke or live integration is enabled."""
        return (
            os.environ.get(LiveTestGuard.LIVE_SMOKE_ENV) == "1"
            or os.environ.get(LiveTestGuard.LIVE_INTEGRATION_ENV) == "1"
        )

    @staticmethod
    def integration_enabled() -> bool:
        """Return True when the live integration (or smoke) gate is set."""
        return LiveTestGuard.smoke_or_integration_enabled()

    @staticmethod
    def configured_base_url() -> Optional[str]:
        """Return ``POSIVERSE_BASE_URL`` when set, otherwise None."""
        raw = os.environ.get(LiveTestGuard.BASE_URL_ENV, "").strip()
        return raw or None

    @staticmethod
    def assert_not_production(url: str) -> str:
        """Normalize ``url`` and refuse the production OpenAPI host.

        Args:
            url: Candidate live-test base URL.

        Returns:
            Normalized https URL with no trailing slash.

        Raises:
            RuntimeError: If the URL points at production.
            ValueError: If the URL is not https or has no host.
        """
        normalized = url.strip().rstrip("/")
        if PosiverseConfig.is_production_host(normalized):
            raise RuntimeError(
                "Live tests refuse the production OpenAPI host. "
                f"Set {LiveTestGuard.BASE_URL_ENV} to your internal test "
                "OpenAPI base URL."
            )
        host = urlparse(normalized).netloc.lower()
        if LiveTestGuard.FORBIDDEN_PROD_HOST in host:
            raise RuntimeError(
                "Live tests refuse the production OpenAPI host. "
                f"Set {LiveTestGuard.BASE_URL_ENV} to your internal test "
                "OpenAPI base URL."
            )
        PosiverseConfig.require_https(normalized)
        return normalized

    @staticmethod
    def require_base_url() -> str:
        """Return the live-test base URL or skip when it is unset.

        Returns:
            Normalized https URL that is not production.

        Raises:
            pytest.skip.Exception: If ``POSIVERSE_BASE_URL`` is unset.
            RuntimeError: If the URL points at production.
            ValueError: If the URL is not https.
        """
        url = LiveTestGuard.configured_base_url()
        if not url:
            pytest.skip(
                f"{LiveTestGuard.BASE_URL_ENV} is required for live tests "
                "(set it to your internal test OpenAPI base URL; "
                "production is refused)"
            )
        return LiveTestGuard.assert_not_production(url)
