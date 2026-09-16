"""Live integration tests for OpenAPI tag Tenants (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_tenants_list(api):
    """GET /tenants — list tenants visible to the API key.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.tenants.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"tenants.list failed: {exc!r}"))
    assert page.items is not None
    assert isinstance(page.items, list)


def test_tenants_get(api, discovered_ids):
    """GET /tenants/{tenantId} — fetch one discovered tenant.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    tenant_id = discovered_ids.get("tenant_id")
    if not tenant_id:
        pytest.skip("no tenant id discovered from GET /tenants")
    tenant = api.tenants.get(tenant_id)
    assert tenant.id == tenant_id


def test_tenants_update_blocked():
    """PUT /tenants/{tenantId} — skipped (non-disposable tenant mutation).

    Raises:
        pytest.skip.Exception: Always; mutating tenants is irreversible /
            unsafe without a disposable fixture.
    """
    pytest.skip("blocked: avoid mutating non-disposable tenants")
