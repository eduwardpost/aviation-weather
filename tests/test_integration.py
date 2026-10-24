from unittest.mock import AsyncMock, patch

from avwx.exceptions import SourceError
import pytest
from homeassistant.config_entries import ConfigEntryState
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


@pytest.mark.parametrize("fail_during_setup", [True, False])
async def test_provider_failure_retries_setup(hass, caplog, fail_during_setup):
    """Both setup fetches expose the upstream error and request a setup retry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Aviation weather for KCON",
        data={CONF_ICAO_ID: "KCON"},
    )
    entry.add_to_hass(hass)
    error = SourceError("NoaaApi server returned 403")
    with patch(
        "custom_components.aviationweather.coordinator.avwx.Metar"
    ) as metar_factory:
        metar_factory.return_value.async_update = AsyncMock(
            side_effect=[error] if fail_during_setup else [None, error]
        )

        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert "NoaaApi server returned 403" in entry.reason
    assert "Unexpected error" not in caplog.text
