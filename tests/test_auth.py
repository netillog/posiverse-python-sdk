"""Tests for API key authentication header behavior."""

from __future__ import annotations

import inspect
import os

import httpx
import pytest

from posiverse import AUTH_HEADER, DEFAULT_BASE_URL, PROD_BASE_URL, PosiverseClient
from posiverse.client import API_KEY_ENV
from posiverse.config import BASE_URL_ENV, PosiverseConfig


def test_auth_header_sent_on_requests(mock_api, client, api_key):
    """Every request must include the posiverse-auth-key header (not Bearer)."""
    route = mock_api.get("/devices").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    client.devices.list()
    assert route.called
    request = route.calls.last.request
    assert request.headers.get(AUTH_HEADER) == api_key
    assert "Authorization" not in request.headers or not request.headers.get(
        "Authorization", ""
    ).lower().startswith("bearer")


def test_api_key_from_env(monkeypatch, mock_api, base_url):
    """Client reads POSIVERSE_API_KEY when api_key argument is omitted."""
    monkeypatch.setenv(API_KEY_ENV, "env-key-value")
    route = mock_api.get("/tenants").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    with PosiverseClient(base_url=base_url) as client:
        client.tenants.list()
    assert route.calls.last.request.headers.get(AUTH_HEADER) == "env-key-value"


def test_api_key_from_dotenv_when_env_unset(monkeypatch, mock_api, base_url, tmp_path):
    """PosiverseClient() reads POSIVERSE_API_KEY from a project-root .env."""
    import posiverse._env as env_module

    monkeypatch.setattr(env_module, "_LOADED", False)
    monkeypatch.setenv(API_KEY_ENV, "sentinel")
    os.environ.pop(API_KEY_ENV, None)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'tmp'\n", encoding="utf-8")
    (tmp_path / ".env").write_text(f'{API_KEY_ENV}="dotenv-key"\n', encoding="utf-8")
    route = mock_api.get("/tenants").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    with PosiverseClient(base_url=base_url) as client:
        client.tenants.list()
    assert route.calls.last.request.headers.get(AUTH_HEADER) == "dotenv-key"


def test_base_url_from_dotenv_when_env_unset(monkeypatch, tmp_path):
    """POSIVERSE_BASE_URL in .env applies when the process environment lacks it."""
    import posiverse._env as env_module

    monkeypatch.setattr(env_module, "_LOADED", False)
    monkeypatch.setenv(BASE_URL_ENV, "sentinel")
    os.environ.pop(BASE_URL_ENV, None)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        'POSIVERSE_BASE_URL="https://from-dotenv.example.invalid"\n',
        encoding="utf-8",
    )
    with PosiverseClient(api_key="k") as client:
        assert client.base_url == "https://from-dotenv.example.invalid"


def test_shell_api_key_wins_over_dotenv(monkeypatch, mock_api, base_url, tmp_path):
    """A key already in the environment is not replaced by .env."""
    import posiverse._env as env_module

    monkeypatch.setattr(env_module, "_LOADED", False)
    monkeypatch.setenv(API_KEY_ENV, "shell-key")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(f"{API_KEY_ENV}=dotenv-key\n", encoding="utf-8")
    route = mock_api.get("/tenants").mock(
        return_value=httpx.Response(200, json=[], headers={"x-total-count": "0"})
    )
    with PosiverseClient(base_url=base_url) as client:
        client.tenants.list()
    assert route.calls.last.request.headers.get(AUTH_HEADER) == "shell-key"


def test_missing_api_key_raises(monkeypatch, base_url):
    """Client raises ValueError when no key is provided or in the environment."""
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(ValueError, match="API key required"):
        PosiverseClient(base_url=base_url)


def test_default_base_url_is_production():
    """Default client base URL must be the production server."""
    with PosiverseClient(api_key="k") as client:
        assert client.base_url == PROD_BASE_URL == DEFAULT_BASE_URL
        assert client.base_url == "https://openapi-prod.posiverse.com"


def test_base_url_env_override(monkeypatch):
    """POSIVERSE_BASE_URL overrides the production default."""
    monkeypatch.setenv(BASE_URL_ENV, "https://internal.example.invalid")
    with PosiverseClient(api_key="k") as client:
        assert client.base_url == "https://internal.example.invalid"


def test_explicit_base_url_wins_over_env(monkeypatch):
    """An explicit base_url argument takes precedence over the env var."""
    monkeypatch.setenv(BASE_URL_ENV, "https://from-env.example.invalid")
    with PosiverseClient(api_key="k", base_url="https://explicit.example.invalid") as client:
        assert client.base_url == "https://explicit.example.invalid"


def test_http_base_url_rejected():
    """Plain HTTP base URLs are not allowed."""
    with pytest.raises(ValueError, match="https"):
        PosiverseClient(api_key="k", base_url="http://openapi.example.invalid")


def test_timeout_none_rejected():
    """Callers cannot disable HTTP timeouts."""
    with pytest.raises(ValueError, match="timeout"):
        PosiverseClient(api_key="k", timeout=None)  # type: ignore[arg-type]


def test_timeout_applied_by_default():
    """Owned httpx clients have a finite default timeout."""
    with PosiverseClient(api_key="k") as client:
        timeout = client._http.timeout
        assert timeout is not None
        assert timeout.connect == PosiverseConfig.DEFAULT_TIMEOUT_SECONDS
        assert timeout.read == PosiverseConfig.DEFAULT_TIMEOUT_SECONDS


def test_verify_true_on_owned_client():
    """Owned httpx clients always verify TLS."""
    with PosiverseClient(api_key="k") as client:
        assert getattr(client._http, "_verify", True) is not False


def test_verify_parameter_not_part_of_public_init():
    """Release paths must not expose a verify= footgun."""
    signature = inspect.signature(PosiverseClient.__init__)
    assert "verify" not in signature.parameters


def test_custom_http_client_verify_false_rejected():
    """A caller-supplied httpx client with verify=False is refused."""
    custom = httpx.Client(base_url="https://openapi.mock.invalid", verify=False, timeout=5.0)
    try:
        with pytest.raises(ValueError, match="verify"):
            PosiverseClient(api_key="k", http_client=custom)
    finally:
        custom.close()


def test_repr_and_str_redact_api_key():
    """repr/str must never include the API key."""
    secret = "super-secret-api-key-value"
    with PosiverseClient(api_key=secret) as client:
        rendered = f"{client!r} {client!s}"
        assert secret not in rendered
        assert PosiverseConfig.REDACTED in rendered
        assert "openapi-prod.posiverse.com" in rendered
