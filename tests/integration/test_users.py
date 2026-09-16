"""Live integration tests for OpenAPI tag Users (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_users_list(api):
    """GET /users — list users for the account tenant.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.users.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"users.list failed: {exc!r}"))
    assert page.items is not None


def test_users_get(api, discovered_ids):
    """GET /users/{userId} — fetch one discovered user.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    user_id = discovered_ids.get("user_id")
    if not user_id:
        pytest.skip("no user id discovered from GET /users")
    user = api.users.get(user_id)
    assert user.id == user_id


def test_users_update_blocked():
    """PUT /users/{userId} — skipped (non-disposable user mutation).

    Raises:
        pytest.skip.Exception: Always; mutating users is unsafe without a
            disposable fixture.
    """
    pytest.skip("blocked: avoid mutating non-disposable users")
