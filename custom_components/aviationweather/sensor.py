"""Platform for sensor integration."""

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPressure, UnitOfSpeed, DEGREE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ICAO_ID, DOMAIN
from .coordinator import AviationWeatherCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    config = config_entry.data
    coordinator: AviationWeatherCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    icao_id = config.get(CONF_ICAO_ID)

    raw_sensor = RawMetarSensor(icao_id, coordinator)
    altimeter_sensor = AltimeterMetarSensor(icao_id, coordinator)
    flightrules_sensor = FlightRulesMetarSensor(icao_id, coordinator)
    visability_sensor = VisabilityMetarSensor(icao_id, coordinator)
    windspeed_sensor = WindSpeedMetarSensor(icao_id, coordinator)
    winddirection_sensor = WindDirectionMetarSensor(icao_id, coordinator)

    async_add_entities(
        [
            raw_sensor,
            altimeter_sensor,
            flightrules_sensor,
            visability_sensor,
            windspeed_sensor,
            winddirection_sensor,
        ]
    )


class RawMetarSensor(SensorEntity):
    """Representation of a raw METAR sensor."""

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_raw"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_raw"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "raw"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._coordinator.data.raw


class AltimeterMetarSensor(SensorEntity):
    """Representation of an altimeter METAR sensor."""

    _attr_native_unit_of_measurement = UnitOfPressure.HPA
    _attr_device_class = SensorDeviceClass.ATMOSPHERIC_PRESSURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_altimeter"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_altimeter"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "altimeter"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._coordinator.data.altimeter.value or None


class WindSpeedMetarSensor(SensorEntity):
    """Representation of an wind_speed METAR sensor."""

    _attr_native_unit_of_measurement = UnitOfSpeed.KNOTS
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_wind_speed"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_wind_speed"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "wind speed"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._coordinator.data.wind_speed.value or None


class WindDirectionMetarSensor(SensorEntity):
    """Representation of an wind_direction METAR sensor."""

    _attr_native_unit_of_measurement = DEGREE
    _attr_device_class = SensorDeviceClass.WIND_DIRECTION
    _attr_state_class = SensorStateClass.MEASUREMENT_ANGLE

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_wind_direction"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_wind_direction"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "wind direction"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._coordinator.data.wind_direction.value or None


class FlightRulesMetarSensor(SensorEntity):
    """Representation of an flight_rules METAR sensor."""

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_flight_rules"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_flight_rules"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "flight rules"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._coordinator.data.flight_rules or None


class VisabilityMetarSensor(SensorEntity):
    """Representation of an visibility METAR sensor."""

    def __init__(self, icao_id: str, coordinator: AviationWeatherCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__()
        self.entity_id = f"sensor.{DOMAIN}_{icao_id.lower()}_visibility"
        self._attr_unique_id = f"{DOMAIN}_{icao_id.lower()}_visibility"
        self._icao_id = icao_id
        self._coordinator = coordinator

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "visability"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._coordinator.data.visibility.value or None
