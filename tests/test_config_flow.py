from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aviationweather.const import CONF_ICAO_ID, DOMAIN


async def test_user_flow_creates_entry(hass):
    """The user flow accepts an ICAO and creates a titled config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert CONF_ICAO_ID in result["data_schema"].schema

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_ICAO_ID: "EHAM"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Aviation weather for EHAM"
    assert result["data"] == {CONF_ICAO_ID: "EHAM"}


async def test_user_flow_rejects_duplicate_icao(hass):
    """An ICAO can only be configured once."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Aviation weather for EHAM",
        data={CONF_ICAO_ID: "EHAM"},
        unique_id="EHAM",
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_ICAO_ID: "EHAM"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
