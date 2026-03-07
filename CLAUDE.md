# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Python script to connect to Aqara APIs for access to virtual devices not exposed via Home Assistant integrations (e.g. infra-red services). The goal is to build a Home Assistant custom integration enabling interaction directly with the infra-red TV remote control Aqara virtual device as a Home Assistant device.

## Running the Script

```bash
python aqara_ir.py
```

## Development Setup

This project uses Python 3.14 (see `.python-version`). It is managed with `pyproject.toml` and `uv`.

To set up a virtual environment:

```bash
uv sync
```

## Aqara SDK Integration

The Aqara OpenAPI is accessed via the [aqara-iot-app-sdk-python](https://github.com/aqara/aqara-iot-app-sdk-python) SDK. It is declared as a dependency in `pyproject.toml`.

Key classes imported from `aqara_iot`:
- `AqaraOpenAPI` — authenticates and communicates with the Aqara cloud endpoint
- `AqaraDeviceManager` — retrieves and manages the device list

The Singapore region is not in the SDK's `AQARA_COUNTRIES` or `APPS` dicts. The workaround is to initialise `AqaraOpenAPI` with `"Europe"` (a valid country code), then immediately overwrite the four instance attributes with Singapore values loaded from `config.yaml`:

```python
openapi = AqaraOpenAPI("Europe")
openapi.endpoint = config["SINGAPORE_ENDPOINT"]
openapi.app_id   = config["APP_ID"]
openapi.app_key  = config["APP_KEY"]
openapi.key_id   = config["KEY_ID"]
```

Credentials and all site-specific settings are loaded from `config.yaml` (not committed):

| Key | Description |
|---|---|
| `username` | Aqara account username |
| `password` | Aqara account password |
| `SINGAPORE_ENDPOINT` | Singapore API base URL |
| `APP_ID` | Singapore app ID |
| `APP_KEY` | Singapore app key |
| `KEY_ID` | Singapore key ID |
| `tv_remote_did` | Device ID of the IR TV remote (prefixed `virtual.`) |

## IR Device API

IR hub virtual devices (device IDs prefixed `virtual.`) are controlled through two intents called directly via `openapi.post("/v3.0/open/api", body)` — the SDK has no IR-specific helper methods:

| Intent | Purpose | Key request fields |
|---|---|---|
| `query.ir.keys` | List all remote control buttons | `did` |
| `write.ir.click` | Press a button | `did`, `keyId` |

`query.ir.keys` returns `result.keys[]`, each with `keyId`, `keyName`, `irKeyId`, and `controllerId`.

Reference: https://opendoc-test.aqara.cn/en/docs/developmanual/apiDocument/IRDeviceManagement.html

## Home Assistant Custom Integration

The integration lives in [custom_components/aqara_ir/](custom_components/aqara_ir/) and exposes the IR TV remote as a **button** entity in Home Assistant. It can be installed via [HACS](https://hacs.xyz) or manually.

### Files

| File | Purpose |
|---|---|
| `hacs.json` | HACS manifest — enables discovery and installation via HACS; `render_readme: true` displays `README.md` as the HACS info page |
| `custom_components/aqara_ir/manifest.json` | Integration metadata and pip requirements |
| `custom_components/aqara_ir/const.py` | `DOMAIN`, config key names, and `POWER_KEY_ID = 1` |
| `custom_components/aqara_ir/__init__.py` | `async_setup` — validates YAML config, authenticates, stores `AqaraOpenAPI` in `hass.data`, loads button platform |
| `custom_components/aqara_ir/button.py` | `AqaraIRPowerButton(ButtonEntity)` — exposes a single **TV Power** button, polls device online state every 30 s |

### Installation via HACS

Add the repository as a custom repository in HACS (Integration category), then download and restart HA.

### Manual Installation

Copy the `custom_components/aqara_ir/` directory into your Home Assistant `custom_components/` folder, then add to `configuration.yaml`:

```yaml
aqara_ir:
  username: peter@dowleys.com
  password: YOUR_PASSWORD
  singapore_endpoint: https://open-sg.aqara.com
  app_id: YOUR_APP_ID
  app_key: YOUR_APP_KEY
  key_id: YOUR_KEY_ID
  tv_remote_did: virtual.51540366390822
```

### Usage

Press the button via the Home Assistant UI, or trigger it from an automation:

```yaml
service: button.press
target:
  entity_id: button.tv_power
```

Pressing the button sends `write.ir.click` with `keyId=1` (Power Supply) to the Aqara IR virtual device. All blocking Aqara SDK calls are dispatched via `hass.async_add_executor_job` to avoid blocking the HA event loop.

### Online / Availability

The entity polls `query.device.info` every 30 seconds (via `SCAN_INTERVAL` and `async_update` in `button.py`). If the Aqara API reports `state == 0` (offline), `_attr_available` is set to `False` and HA marks the entity as **Unavailable** in the UI. It recovers automatically on the next poll when the device comes back online.

## Current Script Behaviour

1. Authenticates with the Aqara OpenAPI using credentials from `config.yaml`.
2. Enumerates all devices, printing name, model, online state, and device ID.
3. Queries IR remote keys for the TV remote device specified by `tv_remote_did` in `config.yaml`.
4. Finds the power key by name and sends a `write.ir.click` command to press it.
