from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfLength, UnitOfPressure

from custom_components.aviationweather.const import DOMAIN
from custom_components.aviationweather.sensor import (
    AltimeterMetarSensor,
    DewpointMetarSensor,
    FlightRulesMetarSensor,
    RawMetarSensor,
    TemperatureMetarSensor,
    TimestampMetarSensor,
    VisibilityMetarSensor,
    WindDirectionMetarSensor,
    WindSpeedMetarSensor,
    async_setup_entry,
)


@pytest.fixture
def metar_coordinator():
    """Provide representative parsed AVWX data and units."""
    timestamp = datetime(2026, 10, 22, 12, 30, tzinfo=UTC)
    data = SimpleNamespace(
        raw="METAR EHAM 221230Z 24010KT 9999 FEW020 15/10 Q1013",
        time=SimpleNamespace(dt=timestamp),
        altimeter=SimpleNamespace(value=1013),
        temperature=SimpleNamespace(value=15),
        dewpoint=SimpleNamespace(value=10),
        flight_rules="VFR",
        visibility=SimpleNamespace(value=10000),
        wind_speed=SimpleNamespace(value=10),
        wind_direction=SimpleNamespace(value=240),
    )
    return SimpleNamespace(
        data=data,
        units=SimpleNamespace(altimeter="hPa", visibility="m"),
    )


@pytest.mark.parametrize(
    ("sensor_class", "key", "expected_value", "expected_unit"),
    [
        (RawMetarSensor, "raw", "METAR EHAM 221230Z 24010KT 9999 FEW020 15/10 Q1013", None),
        (
            TimestampMetarSensor,
            "time",
            datetime(2026, 10, 22, 12, 30, tzinfo=UTC),
            None,
        ),
        (AltimeterMetarSensor, "altimeter", 1013, UnitOfPressure.HPA),
        (TemperatureMetarSensor, "temperature", 15, "°C"),
        (DewpointMetarSensor, "dewpoint", 10, "°C"),
        (FlightRulesMetarSensor, "flight_rules", "VFR", None),
        (VisibilityMetarSensor, "visibility", 10000, UnitOfLength.METERS),
        (WindSpeedMetarSensor, "wind_speed", 10, "kn"),
        (WindDirectionMetarSensor, "wind_direction", 240, "°"),
    ],
)
def test_sensor_values_and_identity(
    metar_coordinator, sensor_class, key, expected_value, expected_unit
):
    """Each sensor exposes its parsed value, stable identity, and device."""
    sensor = sensor_class("EHAM", metar_coordinator)

    assert sensor.native_value == expected_value
    assert sensor.unique_id == f"{DOMAIN}_eham_{key}"
    assert sensor.entity_id == f"sensor.{DOMAIN}_eham_{key}"
    assert sensor.device_info["identifiers"] == {(DOMAIN, "EHAM")}
    if expected_unit is not None:
        assert sensor.native_unit_of_measurement == expected_unit


async def test_setup_adds_nine_sensors(hass, metar_coordinator):
    """Setup creates the established set of nine METAR sensors."""
    config_entry = SimpleNamespace(
        data={"icao_id": "EHAM"},
        entry_id="entry_id",
    )
    hass.data[DOMAIN] = {config_entry.entry_id: metar_coordinator}
    added_entities = []

    await async_setup_entry(hass, config_entry, added_entities.extend)

    assert [entity.entity_id for entity in added_entities] == [
        f"sensor.{DOMAIN}_eham_raw",
        f"sensor.{DOMAIN}_eham_time",
        f"sensor.{DOMAIN}_eham_altimeter",
        f"sensor.{DOMAIN}_eham_temperature",
        f"sensor.{DOMAIN}_eham_dewpoint",
        f"sensor.{DOMAIN}_eham_flight_rules",
        f"sensor.{DOMAIN}_eham_visibility",
        f"sensor.{DOMAIN}_eham_wind_speed",
        f"sensor.{DOMAIN}_eham_wind_direction",
    ]


def test_optional_values_remain_unavailable(metar_coordinator):
    """Optional AVWX values continue to yield no sensor state."""
    metar_coordinator.data.altimeter = None
    metar_coordinator.data.visibility = None

    assert AltimeterMetarSensor("EHAM", metar_coordinator).native_value is None
    assert VisibilityMetarSensor("EHAM", metar_coordinator).native_value is None


def test_wind_direction_metadata_matches_home_assistant_support(metar_coordinator):
    """Use wind direction metadata when the installed Home Assistant supports it."""
    sensor = WindDirectionMetarSensor("EHAM", metar_coordinator)

    assert sensor.device_class == getattr(SensorDeviceClass, "WIND_DIRECTION", None)
    assert sensor.state_class == getattr(SensorStateClass, "MEASUREMENT_ANGLE", None)
