from unittest.mock import AsyncMock, Mock, patch

from avwx.exceptions import SourceError
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aviationweather.const import CONF_ICAO_ID, DOMAIN
from custom_components.aviationweather.coordinator import (
    AviationWeatherCoordinator,
)
from custom_components.aviationweather.sensor import TemperatureMetarSensor


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


@pytest.mark.parametrize("method", ["_async_setup", "_async_update_data"])
@pytest.mark.parametrize(
    "error",
    [
        SourceError("NoaaApi server returned 403"),
        ConnectionError("Unable to connect to NoaaApi server"),
    ],
)
async def test_fetch_errors_use_home_assistant_error_handling(hass, method, error):
    """Expected provider failures retain their cause without unexpected errors."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_ICAO_ID: "KCON"})
    with patch(
        "custom_components.aviationweather.coordinator.avwx.Metar"
    ) as metar_factory:
        metar_factory.return_value.async_update = AsyncMock(side_effect=error)
        coordinator = AviationWeatherCoordinator(hass, entry)

        with pytest.raises(UpdateFailed, match="KCON") as exc_info:
            await getattr(coordinator, method)()

    assert str(error) in str(exc_info.value)
    assert exc_info.value.__cause__ is error


async def test_refresh_failure_and_recovery(hass, caplog):
    """Provider outages mark sensors unavailable, log once, and recover."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_ICAO_ID: "KCON"})
    with patch(
        "custom_components.aviationweather.coordinator.avwx.Metar"
    ) as metar_factory:
        metar = metar_factory.return_value
        metar.async_update = AsyncMock()
        coordinator = AviationWeatherCoordinator(hass, entry)
        sensor = TemperatureMetarSensor("KCON", coordinator)
        await coordinator.async_refresh()
        previous_data = coordinator.data
        assert sensor.available

        metar.async_update.side_effect = SourceError("NoaaApi server returned 403")
        await coordinator.async_refresh()
        await coordinator.async_refresh()

        assert not sensor.available
        assert coordinator.data is previous_data
        assert isinstance(coordinator.last_exception, UpdateFailed)
        assert caplog.text.count("Error fetching") == 1
        assert "Unexpected error" not in caplog.text
        assert "NoaaApi server returned 403" in caplog.text

        metar.async_update.side_effect = None
        await coordinator.async_refresh()

        assert sensor.available
        assert coordinator.data is metar.data
        assert coordinator.units is metar.units


async def test_unexpected_errors_are_not_masked(hass):
    """Programming errors must not be converted into expected fetch failures."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_ICAO_ID: "KCON"})
    with patch(
        "custom_components.aviationweather.coordinator.avwx.Metar"
    ) as metar_factory:
        metar_factory.return_value.async_update = AsyncMock(
            side_effect=ValueError("Unexpected parser failure")
        )
        coordinator = AviationWeatherCoordinator(hass, entry)

        with pytest.raises(ValueError, match="Unexpected parser failure"):
            await coordinator._async_update_data()
