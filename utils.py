"""Meianlike utils."""
import logging

from pymeianlike import Meianlike

from homeassistant import core
from homeassistant.helpers.device_registry import format_mac

_LOGGER = logging.getLogger(__name__)


async def async_get_meianlike_mac(hass: core.HomeAssistant, meianlike: Meianlike) -> str:
    """Retrieve Meianlike MAC address."""
    _LOGGER.debug("Retrieving meianlike mac address")

    mac = await hass.async_add_executor_job(meianlike.get_mac)

    return format_mac(mac)
