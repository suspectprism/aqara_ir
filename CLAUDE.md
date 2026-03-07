# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Python script to connect to Aqara APIs for access to accessories not exposed via Home Assistant integrations (e.g. infra-red services). The goal is to eventually build a Home Assistant plugin enabling automations to interact directly with infra-red Aqara accessories.

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

Credentials (`username`, `password`) and Singapore region API settings (`SINGAPORE_ENDPOINT`, `APP_ID`, `APP_KEY`, `KEY_ID`) are loaded from `config.yaml` (not committed).

## IR Device API

IR hub virtual devices (device IDs prefixed `virtual.`) are controlled through two intents called directly via `openapi.post("/v3.0/open/api", body)` — the SDK has no IR-specific helper methods:

| Intent | Purpose | Key request fields |
|---|---|---|
| `query.ir.keys` | List all remote control buttons | `did` |
| `write.ir.click` | Press a button | `did`, `keyId` |

`query.ir.keys` returns `result.keys[]`, each with `keyId`, `keyName`, `irKeyId`, and `controllerId`.

Reference: https://opendoc-test.aqara.cn/en/docs/developmanual/apiDocument/IRDeviceManagement.html

## Current Script Behaviour

1. Authenticates with the Aqara OpenAPI using credentials from `config.yaml`.
2. Enumerates all devices, printing name, model, online state, and device ID.
3. Queries IR remote keys for device `virtual.51540366390822` (TV remote control).
4. Finds the power key by name and sends a `write.ir.click` command to press it.
