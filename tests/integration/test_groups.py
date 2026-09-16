"""Live integration tests for OpenAPI tag Groups (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_groups_list(api):
    """GET /groups — list groups for the account tenant.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.groups.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"groups.list failed: {exc!r}"))
    assert page.items is not None


def test_groups_get(api, discovered_ids):
    """GET /groups/{groupId} — fetch one discovered group.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    group_id = discovered_ids.get("group_id")
    if not group_id:
        pytest.skip("no group id discovered from GET /groups")
    group = api.groups.get(group_id)
    assert group.id == group_id


def test_groups_update_blocked():
    """PUT /groups/{groupId} — skipped (non-disposable group mutation).

    Raises:
        pytest.skip.Exception: Always; mutating shared groups is unsafe
            without a disposable fixture.
    """
    pytest.skip("blocked: avoid mutating non-disposable groups")
