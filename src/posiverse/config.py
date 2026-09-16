"""Configuration helpers for the Posiverse SDK.

Public consumers talk to production. Staff and bots override the host with
``base_url=`` or ``POSIVERSE_BASE_URL`` so the test hostname does not need
to ship in the package.
"""

from __future__ import annotations

import os
from typing import Optional, Union
from urllib.parse import urlparse

import httpx


class PosiverseConfig:
    """Static helpers for base URL, TLS, timeouts, and secret redaction."""

    PRODUCTION_BASE_URL = "https://openapi-prod.posiverse.com"
    BASE_URL_ENV = "POSIVERSE_BASE_URL"
    API_KEY_ENV = "POSIVERSE_API_KEY"
    AUTH_HEADER = "posiverse-auth-key"
    DEFAULT_TIMEOUT_SECONDS = 30.0
    REDACTED = "***"

    @staticmethod
    def default_timeout() -> httpx.Timeout:
        """Return the SDK default HTTP timeout (never disabled)."""
        return httpx.Timeout(PosiverseConfig.DEFAULT_TIMEOUT_SECONDS)

    @staticmethod
    def coerce_timeout(timeout: Optional[Union[float, httpx.Timeout]]) -> Union[float, httpx.Timeout]:
        """Reject disabled timeouts and otherwise return ``timeout`` unchanged.

        Args:
            timeout: Seconds, an ``httpx.Timeout``, or None.

        Returns:
            The provided timeout value.

        Raises:
            ValueError: If ``timeout`` is None (timeouts cannot be disabled).
        """
        if timeout is None:
            raise ValueError(
                "timeout is required; pass a number of seconds or httpx.Timeout "
                "(the SDK does not allow disabling timeouts)"
            )
        return timeout

    @staticmethod
    def resolve_base_url(base_url: Optional[str] = None) -> str:
        """Resolve the OpenAPI base URL.

        Precedence: explicit ``base_url`` argument, then ``POSIVERSE_BASE_URL``,
        then the production default. HTTP URLs are rejected.

        Args:
            base_url: Optional explicit server URL.

        Returns:
            Normalized https URL with no trailing slash.

        Raises:
            ValueError: If the URL is empty or not https.
        """
        if base_url is None or not str(base_url).strip():
            env_value = os.environ.get(PosiverseConfig.BASE_URL_ENV, "").strip()
            base_url = env_value or PosiverseConfig.PRODUCTION_BASE_URL
        return PosiverseConfig.normalize_base_url(str(base_url))

    @staticmethod
    def normalize_base_url(url: str) -> str:
        """Strip whitespace/trailing slashes and require https.

        Args:
            url: Candidate server URL.

        Returns:
            Normalized https URL with no trailing slash.

        Raises:
            ValueError: If the URL is empty, missing a host, or not https.
        """
        if not isinstance(url, str) or not url.strip():
            raise ValueError("base_url must be a non-empty string")
        normalized = url.strip().rstrip("/")
        PosiverseConfig.require_https(normalized)
        return normalized

    @staticmethod
    def require_https(url: str) -> None:
        """Reject any base URL that is not https.

        Args:
            url: Candidate server URL.

        Raises:
            ValueError: If the scheme is not https or the host is missing.
        """
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError(
                "Base URL must use https; http is not allowed "
                f"(got scheme {parsed.scheme!r})"
            )
        if not parsed.netloc:
            raise ValueError("Base URL must include a host")

    @staticmethod
    def is_production_host(url: str) -> bool:
        """Return True when ``url`` points at the production OpenAPI host.

        Args:
            url: Server URL to inspect.
        """
        host = urlparse(url).netloc.lower()
        if "@" in host:
            host = host.rsplit("@", 1)[-1]
        if ":" in host:
            host = host.split(":", 1)[0]
        return host == urlparse(PosiverseConfig.PRODUCTION_BASE_URL).netloc.lower()

    @staticmethod
    def redact_secret(secret: Optional[str]) -> str:
        """Return a constant redaction token (never the secret).

        Args:
            secret: Unused; accepted so callers can pass the real value safely.
        """
        return PosiverseConfig.REDACTED

    @staticmethod
    def redact_text(text: str, secret: Optional[str]) -> str:
        """Replace ``secret`` in ``text`` when it is non-empty.

        Args:
            text: Arbitrary string that might contain a credential.
            secret: Credential to strip, or None.

        Returns:
            ``text`` with ``secret`` replaced by a redaction token.
        """
        if not secret:
            return text
        return text.replace(secret, PosiverseConfig.REDACTED)


# Public aliases used by the client and package exports.
PROD_BASE_URL = PosiverseConfig.PRODUCTION_BASE_URL
DEFAULT_BASE_URL = PROD_BASE_URL
BASE_URL_ENV = PosiverseConfig.BASE_URL_ENV
API_KEY_ENV = PosiverseConfig.API_KEY_ENV
AUTH_HEADER = PosiverseConfig.AUTH_HEADER
