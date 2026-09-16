"""Live integration tests for OpenAPI tag Products (TEST API only)."""

from __future__ import annotations

import pytest

from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_products_list(api):
    """GET /products — list products.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.products.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"products.list failed: {exc!r}"))
    assert page.items is not None
    assert len(page.items) >= 1


def test_products_get(api, discovered_ids):
    """GET /products/{productId} — fetch one discovered product.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    product_id = discovered_ids.get("product_id")
    if not product_id:
        pytest.skip("no product id discovered from GET /products")
    product = api.products.get(product_id)
    assert product.id == product_id
