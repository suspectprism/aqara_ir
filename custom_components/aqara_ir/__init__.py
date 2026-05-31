"""Aqara IR Remote — Home Assistant custom integration."""
import logging

import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_APP_ID,
    CONF_APP_KEY,
    CONF_KEY_ID,
    CONF_SINGAPORE_ENDPOINT,
    CONF_TV_REMOTE_DID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SINGAPORE_ENDPOINT): cv.string,
                vol.Required(CONF_APP_ID): cv.string,
                vol.Required(CONF_APP_KEY): cv.string,
                vol.Required(CONF_KEY_ID): cv.string,
                vol.Required(CONF_TV_REMOTE_DID): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Aqara IR integration."""
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    openapi = await hass.async_add_executor_job(_setup_openapi, conf)
    if openapi is None:
        _LOGGER.error("Failed to authenticate with Aqara API")
        return False

    hass.data[DOMAIN] = {
        "openapi": openapi,
        "tv_remote_did": conf[CONF_TV_REMOTE_DID],
        "username": conf[CONF_USERNAME],
        "password": conf[CONF_PASSWORD],
    }

    discovery.load_platform(hass, Platform.BUTTON, DOMAIN, {}, config)
    return True


def _setup_openapi(conf):
    """Authenticate with the Aqara API (blocking). Returns AqaraOpenAPI or None."""
    from aqara_iot import AqaraOpenAPI

    # "Singapore" is absent from the SDK's AQARA_COUNTRIES/APPS dicts, so
    # initialise with "Europe" and immediately overwrite the four attributes.
    openapi = AqaraOpenAPI("Europe")
    openapi.endpoint = conf[CONF_SINGAPORE_ENDPOINT]
    openapi.app_id = conf[CONF_APP_ID]
    openapi.app_key = conf[CONF_APP_KEY]
    openapi.key_id = conf[CONF_KEY_ID]

    if not openapi.get_auth(username=conf[CONF_USERNAME], password=conf[CONF_PASSWORD]):
        return None
    return openapi
