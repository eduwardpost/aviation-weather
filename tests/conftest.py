pytest_plugins = "pytest_homeassistant_custom_component"


import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Register the integration as a custom integration for Home Assistant tests."""
