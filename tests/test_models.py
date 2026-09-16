"""Tests for Pydantic models derived from OpenAPI component schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from posiverse.models import (
    Device,
    Error,
    SettingsData,
    TagMapPut,
    TagPut,
    TelemetryLog,
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
    """OpenAPI field ``json`` maps to ``json_`` on TelemetryLog."""
    log = TelemetryLog.model_validate({"imei": "1", "json": '{"x":1}'})
    assert log.json_ == '{"x":1}'
    dumped = log.model_dump(by_alias=True)
    assert dumped["json"] == '{"x":1}'
    assert "json_" not in dumped


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


def test_settings_data_extra_fields_allowed():
    """Unknown settings keys are preserved for forward compatibility."""
    data = SettingsData.model_validate({"ver": 1, "futureFlag": True})
    assert data.ver == 1
    assert data.futureFlag is True
