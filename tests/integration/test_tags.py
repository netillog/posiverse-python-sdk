"""Live integration tests for OpenAPI tag Tags (TEST API only).

Creates a disposable tag, updates it, and deletes it. Skips if create is
forbidden by the API key permissions.
"""

from __future__ import annotations

import uuid

import pytest

from posiverse.errors import APIError, BadRequestError, ForbiddenError
from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_tags_list(api):
    """GET /tags - list tags for the account tenant.

    Args:
        api: Throttled live PosiverseClient fixture.
    """
    try:
        page = api.tags.list()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"tags.list failed: {exc!r}"))
    assert page.items is not None


def test_tags_get_existing(api, discovered_ids):
    """GET /tags/{tagId} - fetch one existing tag when available.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
    """
    tag_id = discovered_ids.get("tag_id")
    if not tag_id:
        pytest.skip("no existing tag id discovered from GET /tags")
    tag = api.tags.get(tag_id)
    assert tag.id == tag_id


def test_tags_create_update_delete(api, throttle):
    """POST/PUT/DELETE /tags - disposable tag lifecycle.

    Args:
        api: Throttled live PosiverseClient fixture.
        throttle: Shared request throttle.
    """
    suffix = uuid.uuid4().hex[:8]
    name = f"sdk-live-int-{suffix}"
    created = None
    try:
        try:
            created = api.tags.create({"name": name})
        except ForbiddenError as exc:
            pytest.skip(scrub_secrets(f"tags.create forbidden: {exc}"))
        except BadRequestError as exc:
            pytest.skip(scrub_secrets(f"tags.create bad request: {exc}"))
        except APIError as exc:
            pytest.skip(scrub_secrets(f"tags.create unavailable: {exc}"))

        assert created is not None
        assert created.id
        assert created.name == name

        throttle.wait()
        fetched = api.tags.get(created.id)
        assert fetched.id == created.id

        new_name = f"{name}-renamed"
        throttle.wait()
        api.tags.update(created.id, {"name": new_name})

        throttle.wait()
        renamed = api.tags.get(created.id)
        assert renamed.name == new_name
    finally:
        if created is not None and created.id:
            throttle.wait()
            try:
                api.tags.delete(created.id)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(scrub_secrets(f"tags.delete cleanup failed: {exc!r}"))
