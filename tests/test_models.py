"""Tests for Pydantic models derived from OpenAPI component schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from posiverse.models import (
    ConsoleLine,
    Device,
    DeviceLog,
    DevicePut,
    Error,
    SettingsData,
    SettingsSynched,
    TagMapPut,
    TagPut,
    TelemetryLog,
    User,
    UserLog,
)


def test_device_nested_full_payload():
    """Device.full nested objects validate as typed models."""
    device = Device.model_validate(
        {
            "id": "d1",
            "scratchpad": {"ver": 2, "engineHrsCalc": 1.5},
            "properties": {"vin": "WVW"},
            "settings": {"ver": 1, "config": {"interval": 60}},
        }
    )
    assert device.scratchpad.ver == 2
    assert device.scratchpad.engineHrsCalc == 1.5
    assert device.properties.vin == "WVW"
    assert device.settings.config.interval == 60


def test_telemetry_json_alias():
    """OpenAPI field ``json`` maps to ``json_`` on TelemetryLog and is an object."""
    log = TelemetryLog.model_validate({"imei": "1", "json": {"x": 1}})
    assert log.json_ == {"x": 1}
    dumped = log.model_dump(by_alias=True)
    assert dumped["json"] == {"x": 1}
    assert "json_" not in dumped
    with pytest.raises(ValidationError):
        TelemetryLog.model_validate({"json": '{"x":1}'})


def test_tag_put_requires_name():
    """TagPut.name is required by the OpenAPI schema."""
    with pytest.raises(ValidationError):
        TagPut()
    assert TagPut(name="fleet").name == "fleet"


def test_tag_map_put_requires_value():
    """TagMapPut.value is required by the OpenAPI schema."""
    with pytest.raises(ValidationError):
        TagMapPut()
    assert TagMapPut(value="west").value == "west"


def test_error_schema_required_fields():
    """Error.code and Error.message are required."""
    with pytest.raises(ValidationError):
        Error(code=400)
    err = Error(code=404, message="missing")
    assert err.code == 404


def test_device_log_result_and_request_are_objects():
    """OpenAPI types request and result as objects (or null when omitted)."""
    as_object = DeviceLog.model_validate(
        {
            "deviceId": "d1",
            "database": "db-1",
            "request": {"imei": "123", "ts": 1, "rpt": {"b": 2, "a": 1}},
            "result": {"ok": True, "n": 2, "nested": {"k": "v"}},
        }
    )
    assert as_object.database == "db-1"
    assert as_object.request == {"imei": "123", "ts": 1, "rpt": {"b": 2, "a": 1}}
    assert as_object.result == {"ok": True, "n": 2, "nested": {"k": "v"}}
    assert as_object.model_dump()["result"] == {"ok": True, "n": 2, "nested": {"k": "v"}}

    empty_object = DeviceLog.model_validate({"result": {}, "request": {}})
    assert empty_object.result == {}
    assert empty_object.request == {}

    with pytest.raises(ValidationError):
        DeviceLog.model_validate({"request": '{"ts":1}', "result": "diagnostic"})

    as_null = DeviceLog.model_validate({"request": None, "result": None})
    assert as_null.request is None
    assert as_null.result is None

    omitted = DeviceLog.model_validate({"deviceId": "d1"})
    assert omitted.request is None
    assert omitted.result is None


def test_user_log_and_user_language_match_spec():
    """User.language and UserLog.database/request/result follow the OpenAPI names."""
    user = User.model_validate({"id": "u1", "language": "en"})
    assert user.language == "en"
    log = UserLog.model_validate(
        {"userId": "u1", "database": "db", "request": {"a": 1}, "result": {}}
    )
    assert log.database == "db"
    assert log.request == {"a": 1}
    with pytest.raises(ValidationError):
        UserLog.model_validate({"request": "not-an-object"})


def test_device_vcm_and_settings_synched_fields():
    """Device VCM fields and SettingsSynched.ver match the OpenAPI names."""
    device = Device.model_validate(
        {
            "id": "d1",
            "isVcmStatic": True,
            "vcmProtocolId": "p1",
            "vcmProtocolId2": "p2",
            "vcmVehicleId": "v1",
        }
    )
    assert device.isVcmStatic is True
    assert device.vcmProtocolId2 == "p2"
    body = DevicePut(isVcmStatic=False, vcmProtocol2Id="p2")
    dumped = body.model_dump(exclude_none=True)
    assert dumped["vcmProtocol2Id"] == "p2"
    assert "vcmProtocolId2" not in dumped
    synched = SettingsSynched.model_validate({"ver": 3, "errors": {"field": "bad"}})
    assert synched.ver == 3
    assert synched.errors == {"field": "bad"}
    line = ConsoleLine.model_validate({"date": 1, "idx": 2, "data": "ok"})
    assert line.idx == 2


def test_settings_data_extra_fields_allowed():
    """Unknown settings keys are preserved for forward compatibility."""
    data = SettingsData.model_validate({"ver": 1, "futureFlag": True})
    assert data.ver == 1
    assert data.futureFlag is True
