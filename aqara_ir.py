# Aqara IR - connect to Aqara APIs for access to unpublished accessories such as infra-red services
#
# Peter Dowley
# v 0.1.0
# 7 Mar 2026

import yaml

from aqara_iot import AqaraDeviceManager, AqaraOpenAPI

# Singapore is not built into the default SDK's country list, so I need to use the EUROPE endpoint and override it
# Using the SINGAPORE_ENDPOINT, APP_ID, APP_KEY and KEY_ID from config.yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    config:dict = load_config()

    # "Singapore" is not in the SDK's AQARA_COUNTRIES or APPS dicts, so initialise
    # with "Europe" to satisfy the constructor, then override with Singapore settings.
    openapi = AqaraOpenAPI("Europe")
    openapi.endpoint = config["SINGAPORE_ENDPOINT"]
    openapi.app_id = config["APP_ID"]
    openapi.app_key = config["APP_KEY"]
    openapi.key_id = config["KEY_ID"]

    print(f"Connecting to {openapi.endpoint} ...")
    if not openapi.get_auth(username=config["username"], password=config["password"]):
        print("Authentication failed.")
        return

    print("Authenticated successfully.")

    device_manager = AqaraDeviceManager(openapi)
    device_manager.generate_devices_and_update_value()

    print(f"\nFound {len(device_manager.device_map)} device(s):")
    for did, device in device_manager.device_map.items():
        state = "online" if device.state == 1 else "offline"
        print(f"  [{state}] {device.device_name} ({device.model}) - {did}")

    target_did = "virtual.51540366390822"
    target_device = device_manager.get_device(target_did)
    if target_device is None:
        print(f"\nDevice {target_did} not found.")
        return

    # Query the IR remote control keys available for this device
    ir_keys_resp = openapi.post(
        "/v3.0/open/api",
        {"intent": "query.ir.keys", "data": {"did": target_did}},
    )
    if ir_keys_resp is None or ir_keys_resp.get("code") != 0:
        print(f"\nFailed to query IR keys: {ir_keys_resp}")
        return

    ir_keys = ir_keys_resp.get("result", {}).get("keys", [])
    print(f"\nIR keys for {target_device.device_name}:")
    for key in ir_keys:
        print(f"  keyId={key.get('keyId')}  {key.get('keyName')}")

    # Find and press the power key
    power_key = next(
        (k for k in ir_keys if "power" in k.get("keyName", "").lower()),
        None,
    )
    if power_key is None:
        print("\nNo power key found.")
        return

    # IR key with keyId=1 for our TV is called Power Supply
    print(f"\nPressing '{power_key.get('keyName')}' (keyId={power_key.get('keyId')}) ...")
    click_resp = openapi.post(
        "/v3.0/open/api",
        {"intent": "write.ir.click", "data": {"did": target_did, "keyId": power_key.get("keyId")}},
    )
    if click_resp is not None and click_resp.get("code") == 0:
        print("Command sent successfully.")
    else:
        print(f"Command failed: {click_resp}")

if __name__ == "__main__":
    main()
