from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aviationweather import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.aviationweather.const import CONF_ICAO_ID, DOMAIN


async def test_setup_and_unload_entry(hass):
    """Setup refreshes and forwards the entry; unload removes its coordinator."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Aviation weather for EHAM",
        data={CONF_ICAO_ID: "EHAM"},
    )
    coordinator = AsyncMock()

    with (
        patch(
            "custom_components.aviationweather.AviationWeatherCoordinator",
            return_value=coordinator,
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", new_callable=AsyncMock
        ) as forward_setups,
        patch.object(
            hass.config_entries, "async_unload_platforms", new_callable=AsyncMock
        ) as unload_platforms,
    ):
        assert await async_setup_entry(hass, config_entry)
        coordinator.async_config_entry_first_refresh.assert_awaited_once()
        forward_setups.assert_awaited_once()
        assert hass.data[DOMAIN][config_entry.entry_id] is coordinator

        unload_platforms.return_value = True
        assert await async_unload_entry(hass, config_entry)

    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_failed_unload_keeps_coordinator(hass):
    """Keep coordinator data available when Home Assistant cannot unload platforms."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Aviation weather for EHAM",
        data={CONF_ICAO_ID: "EHAM"},
    )
    coordinator = AsyncMock()
    hass.data[DOMAIN] = {config_entry.entry_id: coordinator}

    with patch.object(
        hass.config_entries, "async_unload_platforms", new_callable=AsyncMock
    ) as unload_platforms:
        unload_platforms.return_value = False

        assert not await async_unload_entry(hass, config_entry)

    assert hass.data[DOMAIN][config_entry.entry_id] is coordinator
