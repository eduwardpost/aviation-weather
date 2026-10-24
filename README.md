# Aviation weather HACS integration

## About

This integration exposes Metar data in HomeAssistant using AVWX.

## Installation

Installation is done like any other Home Assistant HACS integration.

### Requirements

In order to setup this integration you will need:

- A Home Assistant instance with [HACS](https://hacs.xyz/) installed.

### HACS Installation

Search for "Aviation weather" in the HACS store. If you don't see it there, you can [add this repository url as a HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/eduwardpost/aviation-weather)

## Home Assistant Integration

[![Open your Home Assistant instance and start setting up a new integration of a specific brand.](https://my.home-assistant.io/badges/brand.svg)](https://my.home-assistant.io/redirect/brand/?brand=+aviationweather)

After installation, setup the integration via the web UI like any other integration. When prompted, provide the following:

### ICAO Code

- The ICAO Code (ex. EHAM) in upper case letters

## Contributions

Contributions are welcome!

### Running tests

Install the test dependencies and run the test suite from the repository root:

```bash
python -m pip install -r requirements_test.txt
pytest
```
### Dev container

The repository includes a [dev container](.devcontainer/devcontainer.json) with Python and a pre-installed Home Assistant (same version as the test dependencies).

1. Open the repository in VS Code and choose **Reopen in Container**.
2. Start Home Assistant with this integration loaded:
   - **Debugging:** Run and Debug → **Home Assistant (debug)** (breakpoints in `custom_components/aviationweather` work).
   - **Without debugger:** run `.devcontainer/scripts/develop` (or the **Run Home Assistant on port 8123** task).
3. Open <http://localhost:8123>, complete onboarding, and add the **AVWX** integration under *Settings → Devices & services*.

The Home Assistant config lives in [`.devcontainer/config/`](.devcontainer/config/configuration.yaml); runtime files created there are ignored by git.
