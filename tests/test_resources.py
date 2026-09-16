"""Mocked tests covering every OpenAPI tag resource."""

from __future__ import annotations

import httpx
import pytest

from posiverse.models import DevicePut, SettingsPut, TagMapPut, TagPut


def test_commands_list_add_delete(mock_api, client):
    """Commands GET/POST/DELETE /commands/{deviceId}."""
    mock_api.get("/commands/dev-1").mock(
        return_value=httpx.Response(
            200, json=[{"id": "c1", "deviceId": "dev-1", "command": "reset"}]
        )
    )
    commands = client.commands.list("dev-1")
    assert commands[0].command == "reset"

    post = mock_api.post("/commands/dev-1").mock(return_value=httpx.Response(200))
    client.commands.add("dev-1", "reset")
    assert post.calls.last.request.headers["content-type"].startswith("text/plain")
    assert post.calls.last.request.content == b"reset"

    delete = mock_api.delete("/commands/dev-1").mock(return_value=httpx.Response(200))
    client.commands.delete("dev-1")
    assert delete.called


def test_devices_list_get_update_nested(mock_api, client):
    """Devices list/get/update plus properties, scratchpad, settings synched."""
    mock_api.get("/devices").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "d1", "imei": "123"}],
            headers={"x-total-count": "1"},
        )
    )
    page = client.devices.list(group_id="g1", imei="123", full=True, tenant_id="t1")
    assert page.items[0].imei == "123"
    assert "groupId=g1" in str(mock_api.calls.last.request.url)
    assert "full=true" in str(mock_api.calls.last.request.url)

    mock_api.get("/devices/d1").mock(
        return_value=httpx.Response(200, json={"id": "d1", "name": "Truck"})
    )
    device = client.devices.get("d1", full=True)
    assert device.name == "Truck"

    put = mock_api.put("/devices/d1").mock(return_value=httpx.Response(200))
    client.devices.update("d1", DevicePut(name="Renamed"))
    assert put.calls.last.request.content
    assert b"Renamed" in put.calls.last.request.content

    mock_api.get("/properties/d1").mock(
        return_value=httpx.Response(200, json={"ver": 3, "data": {"vin": "V"}})
    )
    props = client.devices.get_properties("d1")
    assert props.ver == 3
    assert props.data.vin == "V"

    mock_api.get("/scratchpads/d1").mock(
        return_value=httpx.Response(200, json={"ver": 1, "totalFuel": 10})
    )
    pad = client.devices.get_scratchpad("d1")
    assert pad.totalFuel == 10

    mock_api.get("/settingssynched/d1").mock(
        return_value=httpx.Response(200, json={"version": 2, "data": {"ver": 1}})
    )
    synched = client.devices.get_settings_synched("d1")
    assert synched.version == 2


def test_firmwares_and_products(mock_api, client):
    """Firmwares and Products list/get."""
    mock_api.get("/firmwares").mock(
        return_value=httpx.Response(200, json=[{"id": "f1", "type": "main"}])
    )
    mock_api.get("/firmwares/f1").mock(
        return_value=httpx.Response(200, json={"id": "f1", "version": "1.0"})
    )
    assert client.firmwares.list().items[0].type == "main"
    assert client.firmwares.get("f1").version == "1.0"

    mock_api.get("/products").mock(
        return_value=httpx.Response(200, json=[{"id": "p1", "name": "OT-2"}])
    )
    mock_api.get("/products/p1").mock(
        return_value=httpx.Response(200, json={"id": "p1", "name": "OT-2"})
    )
    assert client.products.list().items[0].name == "OT-2"
    assert client.products.get("p1").id == "p1"


def test_groups_users_tenants(mock_api, client):
    """Groups, Users, and Tenants list/get/update."""
    mock_api.get("/groups").mock(return_value=httpx.Response(200, json=[{"id": "g1"}]))
    mock_api.get("/groups/g1").mock(
        return_value=httpx.Response(200, json={"id": "g1", "name": "Fleet"})
    )
    mock_api.put("/groups/g1").mock(return_value=httpx.Response(200))
    assert client.groups.list().items[0].id == "g1"
    assert client.groups.get("g1").name == "Fleet"
    client.groups.update("g1", {"name": "Fleet 2"})

    mock_api.get("/users").mock(return_value=httpx.Response(200, json=[{"id": "u1"}]))
    mock_api.get("/users/u1").mock(
        return_value=httpx.Response(200, json={"id": "u1", "name": "Ada"})
    )
    mock_api.put("/users/u1").mock(return_value=httpx.Response(200))
    assert client.users.list().items[0].id == "u1"
    assert client.users.get("u1").name == "Ada"
    client.users.update("u1", {"description": "admin"})

    mock_api.get("/tenants").mock(return_value=httpx.Response(200, json=[{"id": "t1"}]))
    mock_api.get("/tenants/t1").mock(
        return_value=httpx.Response(200, json={"id": "t1", "name": "Acme"})
    )
    mock_api.put("/tenants/t1").mock(return_value=httpx.Response(200))
    assert client.tenants.list().items[0].id == "t1"
    assert client.tenants.get("t1").name == "Acme"
    client.tenants.update("t1", {"name": "Acme Inc"})


def test_settings_get_update(mock_api, client):
    """Settings GET/PUT /settings/{ownerId}."""
    mock_api.get("/settings/own-1").mock(
        return_value=httpx.Response(200, json={"ver": 4, "data": {"ver": 1}})
    )
    settings = client.settings.get("own-1")
    assert settings.ver == 4

    put = mock_api.put("/settings/own-1").mock(return_value=httpx.Response(200))
    client.settings.update("own-1", SettingsPut(config={"feature": 1}))
    assert put.called


def test_tags_and_tagmaps(mock_api, client):
    """Tags CRUD and TagMaps CRUD."""
    mock_api.get("/tags").mock(
        return_value=httpx.Response(200, json=[{"id": "tg", "name": "region"}])
    )
    mock_api.post("/tags").mock(
        return_value=httpx.Response(200, json={"id": "tg", "name": "region"})
    )
    mock_api.get("/tags/tg").mock(
        return_value=httpx.Response(200, json={"id": "tg", "name": "region"})
    )
    mock_api.put("/tags/tg").mock(return_value=httpx.Response(200))
    mock_api.delete("/tags/tg").mock(return_value=httpx.Response(200))

    assert client.tags.list().items[0].name == "region"
    created = client.tags.create(TagPut(name="region"))
    assert created.id == "tg"
    assert client.tags.get("tg").name == "region"
    client.tags.update("tg", {"name": "region-2"})
    client.tags.delete("tg")

    mock_api.get("/tagmaps/tg").mock(
        return_value=httpx.Response(200, json=[{"tagId": "tg", "ownerId": "d1", "value": "west"}])
    )
    mock_api.get("/tagmaps/tg/d1").mock(
        return_value=httpx.Response(200, json={"tagId": "tg", "ownerId": "d1", "value": "west"})
    )
    mock_api.post("/tagmaps/tg/d1").mock(
        return_value=httpx.Response(200, json={"tagId": "tg", "ownerId": "d1", "value": "west"})
    )
    mock_api.put("/tagmaps/tg/d1").mock(
        return_value=httpx.Response(200, json={"tagId": "tg", "ownerId": "d1", "value": "east"})
    )
    mock_api.delete("/tagmaps/tg/d1").mock(return_value=httpx.Response(200))

    assert client.tagmaps.list("tg").items[0].value == "west"
    assert client.tagmaps.get("tg", "d1").ownerId == "d1"
    assert client.tagmaps.create("tg", "d1", TagMapPut(value="west")).value == "west"
    assert client.tagmaps.update("tg", "d1", {"value": "east"}).value == "east"
    client.tagmaps.delete("tg", "d1")


def test_logs_device_telemetry_user(mock_api, client):
    """Logs endpoints including the imeis XOR deviceIds guard."""
    mock_api.get("/devicelogs").mock(
        return_value=httpx.Response(200, json=[{"deviceId": "d1", "imei": "123"}])
    )
    page = client.logs.list_device(start_millis=1, imeis="123")
    assert page.items[0].imei == "123"
    url = str(mock_api.calls.last.request.url)
    assert "imeis=123" in url
    assert "startMillis=1" in url

    with pytest.raises(ValueError, match="exactly one"):
        client.logs.list_device(start_millis=1)
    with pytest.raises(ValueError, match="exactly one"):
        client.logs.list_device(start_millis=1, imeis="1", device_ids="d1")

    mock_api.get("/telemetrylogs").mock(
        return_value=httpx.Response(200, json=[{"imei": "123", "json": '{"a":1}'}])
    )
    tel = client.logs.list_telemetry(start_millis=1, imeis=["123"])
    assert tel.items[0].json_ == '{"a":1}'

    mock_api.get("/userlogs").mock(
        return_value=httpx.Response(200, json=[{"userId": "u1", "action": "login"}])
    )
    users = client.logs.list_user(start_millis=1, user_ids="u1")
    assert users.items[0].action == "login"


def test_virtual_console(mock_api, client):
    """VirtualConsole GET output and PUT command query param."""
    mock_api.get("/virtualconsole/d1").mock(
        return_value=httpx.Response(200, json=[{"date": 0, "idx": 1, "data": "ok"}])
    )
    lines = client.virtual_console.get_output("d1", last_date=0)
    assert lines[0].data == "ok"
    assert "lastDate=0" in str(mock_api.calls.last.request.url)

    put = mock_api.put("/virtualconsole/d1").mock(return_value=httpx.Response(200))
    client.virtual_console.send("d1", "ati")
    assert "command=ati" in str(put.calls.last.request.url)
