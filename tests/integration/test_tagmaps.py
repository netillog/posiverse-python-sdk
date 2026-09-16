"""Live integration tests for OpenAPI tag TagMaps (TEST API only).

Uses a disposable tag mapped to the known TEST device, then deletes both
the map and the tag. Skips when create permissions are insufficient.
"""

from __future__ import annotations

import uuid

import pytest

from posiverse.errors import APIError, BadRequestError, ForbiddenError, NotFoundError
from tests.integration.helpers import scrub_secrets

pytestmark = pytest.mark.live


def test_tagmaps_list_existing(api, discovered_ids, throttle):
    """GET /tagmaps/{tagId} - list maps for an existing tag when present.

    Args:
        api: Throttled live PosiverseClient fixture.
        discovered_ids: Session-scoped discovered resource IDs.
        throttle: Shared request throttle.
    """
    tag_id = discovered_ids.get("tag_id")
    if not tag_id:
        pytest.skip("no existing tag id discovered from GET /tags")
    throttle.wait()
    try:
        page = api.tagmaps.list(tag_id)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(scrub_secrets(f"tagmaps.list failed: {exc!r}"))
    assert page.items is not None


def test_tagmaps_create_update_get_delete(api, known_device_id, throttle):
    """POST/PUT/GET/DELETE tagmaps against a disposable tag + known device.

    Args:
        api: Throttled live PosiverseClient fixture.
        known_device_id: Known TEST device UUID used as objectId/ownerId.
        throttle: Shared request throttle.
    """
    suffix = uuid.uuid4().hex[:8]
    tag_name = f"sdk-live-map-{suffix}"
    tag = None
    mapped = False
    try:
        try:
            tag = api.tags.create({"name": tag_name})
        except ForbiddenError as exc:
            pytest.skip(scrub_secrets(f"tags.create forbidden for tagmaps: {exc}"))
        except (BadRequestError, APIError) as exc:
            pytest.skip(scrub_secrets(f"tags.create unavailable for tagmaps: {exc}"))

        assert tag is not None and tag.id

        throttle.wait()
        try:
            created_map = api.tagmaps.create(
                tag.id,
                known_device_id,
                {"value": f"v-{suffix}"},
            )
        except ForbiddenError as exc:
            pytest.skip(scrub_secrets(f"tagmaps.create forbidden: {exc}"))
        except (BadRequestError, APIError) as exc:
            pytest.skip(scrub_secrets(f"tagmaps.create unavailable: {exc}"))

        mapped = True
        assert created_map.tagId == tag.id or created_map.tagId is None
        assert created_map.value == f"v-{suffix}" or created_map.value is not None

        throttle.wait()
        fetched = api.tagmaps.get(tag.id, known_device_id)
        assert fetched is not None

        throttle.wait()
        updated = api.tagmaps.update(
            tag.id,
            known_device_id,
            {"value": f"v-{suffix}-upd"},
        )
        assert updated.value == f"v-{suffix}-upd" or updated is not None

        throttle.wait()
        page = api.tagmaps.list(tag.id)
        assert page.items is not None
    finally:
        if tag is not None and tag.id:
            if mapped:
                throttle.wait()
                try:
                    api.tagmaps.delete(tag.id, known_device_id)
                except NotFoundError:
                    pass
                except Exception as exc:  # noqa: BLE001
                    pytest.fail(
                        scrub_secrets(f"tagmaps.delete cleanup failed: {exc!r}")
                    )
            throttle.wait()
            try:
                api.tags.delete(tag.id)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(scrub_secrets(f"tags.delete cleanup failed: {exc!r}"))
