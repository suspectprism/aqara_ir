# Aqara IR Remote — Home Assistant Custom Integration

A Home Assistant custom integration that exposes an Aqara IR TV remote virtual device as a **button** entity, allowing automations to send IR Power key presses via the Aqara cloud API.

## Requirements

- An Aqara account with an IR hub and a configured TV virtual device
- Aqara OpenAPI credentials (App ID, App Key, Key ID) from the [Aqara Developer Console](https://developer.aqara.com)
- The virtual device ID of your TV IR remote (prefixed `virtual.`)

## Installation via HACS

1. In Home Assistant, open **HACS → Integrations**.
2. Click the three-dot menu (top right) and choose **Custom repositories**.
3. Enter the repository URL and select **Integration** as the category, then click **Add**.
4. Search for **Aqara IR Remote** and click **Download**.
5. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
aqara_ir:
  username: YOUR_AQARA_EMAIL
  password: YOUR_AQARA_PASSWORD
  singapore_endpoint: https://open-sg.aqara.com
  app_id: YOUR_APP_ID
  app_key: YOUR_APP_KEY
  key_id: YOUR_KEY_ID
  tv_remote_did: virtual.XXXXXXXXXXXXXXXXX
```

Restart Home Assistant after adding the configuration.

## Usage

A `button.tv_power` entity will appear in Home Assistant. Press it from the UI or trigger it from an automation:

```yaml
service: button.press
target:
  entity_id: button.tv_power
```

The button shows as **Unavailable** when the Aqara IR virtual device reports offline, and recovers automatically when it comes back online. If the Aqara API session token expires, the integration re-authenticates automatically without requiring a Home Assistant restart.

## Development

A standalone test script (`aqara_ir.py`) is included for verifying API connectivity outside of Home Assistant. See `CLAUDE.md` for full developer guidance.
