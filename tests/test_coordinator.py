from unittest.mock import AsyncMock, Mock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aviationweather.const import CONF_ICAO_ID, DOMAIN
from custom_components.aviationweather.coordinator import (
    AviationWeatherCoordinator,
)


async def test_coordinator_fetches_metar_and_exposes_units(hass):
    """The coordinator updates AVWX and returns its parsed METAR data."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Aviation weather for EHAM",
        data={CONF_ICAO_ID: "EHAM"},
    )
    metar = Mock()
    metar.async_update = AsyncMock()
    metar.units = Mock()
    metar.data = Mock()

    with patch(
        "custom_components.aviationweather.coordinator.avwx.Metar",
        return_value=metar,
    ) as metar_factory:
        coordinator = AviationWeatherCoordinator(hass, config_entry)
        await coordinator._async_setup()
        result = await coordinator._async_update_data()

    metar_factory.assert_called_once_with("EHAM")
    assert metar.async_update.await_count == 2
    assert coordinator.units is metar.units
    assert result is metar.data
