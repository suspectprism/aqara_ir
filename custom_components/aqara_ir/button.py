"""Aqara IR Remote — button platform."""
import logging
from datetime import timedelta

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN, POWER_KEY_ID

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Aqara IR power button platform."""
    if discovery_info is None:
        return

    data = hass.data[DOMAIN]
    openapi = data["openapi"]
    did = data["tv_remote_did"]

    async_add_entities([AqaraIRPowerButton(hass, openapi, did)], True)


def _fetch_device_online(openapi, did):
    """Return True if the Aqara API reports the device as online (blocking)."""
    resp = openapi.post(
        "/v3.0/open/api",
        {"intent": "query.device.info", "data": {"dids": [did], "positionId": "", "pageNum": 1, "pageSize": 1}},
    )
    if resp and resp.get("code") == 0:
        data = resp.get("result", {}).get("data", [])
        if data:
            return data[0].get("state", 0) == 1
    return False


class AqaraIRPowerButton(ButtonEntity):
    """A Home Assistant button that presses the Power key on the Aqara IR TV remote."""

    def __init__(self, hass, openapi, did):
        self._hass = hass
        self._openapi = openapi
        self._did = did
        self._attr_name = "TV Power"
        self._attr_unique_id = f"aqara_ir_{did}_power"
        self._attr_available = True

    async def async_update(self):
        """Poll the Aqara API for the device's online state."""
        online = await self._hass.async_add_executor_job(
            _fetch_device_online, self._openapi, self._did
        )
        self._attr_available = online
        if not online:
            _LOGGER.warning("Aqara IR device %s is offline", self._did)

    async def async_press(self):
        """Send the Power key press to the Aqara IR virtual device."""
        await self._hass.async_add_executor_job(self._send_power)

    def _send_power(self):
        """Send the power IR command (blocking)."""
        resp = self._openapi.post(
            "/v3.0/open/api",
            {"intent": "write.ir.click", "data": {"did": self._did, "keyId": POWER_KEY_ID}},
        )
        if resp is None or resp.get("code") != 0:
            _LOGGER.error("Failed to send power command: %s", resp)
