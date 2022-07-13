"""Meianlike integration."""
from __future__ import annotations

import asyncio
import logging

from async_timeout import timeout
from pymeianlike import (
    Meianlike,
    MeianlikeGenericException,
    MeianlikeSocketTimeoutException,
)

from homeassistant.components.alarm_control_panel import SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .utils import async_get_meianlike_mac

PLATFORMS = [Platform.ALARM_CONTROL_PANEL]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meianlike config."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    meianlike = Meianlike(username, password, host, port)

    try:
        async with timeout(10):
            meianlike_mac = await async_get_meianlike_mac(hass, meianlike)
    except (
        asyncio.TimeoutError,
        ConnectionError,
        MeianlikeGenericException,
        MeianlikeSocketTimeoutException,
    ) as ex:
        raise ConfigEntryNotReady from ex

    coordinator = MeianlikeDataUpdateCoordinator(hass, meianlike, meianlike_mac)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Meianlike config."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MeianlikeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Meianlike data."""

    def __init__(self, hass: HomeAssistant, meianlike: Meianlike, mac: str) -> None:
        """Initialize global a Meianlike data updater."""
        self.meianlike: Meianlike = meianlike
        self.state: int | None = None
        self.host: str = meianlike.host
        self.mac: str = mac

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    def _update_data(self) -> None:
        """Fetch data from Meianlike via sync functions."""
        status: int = self.meianlike.get_status()
        _LOGGER.debug("Meianlike status: %s", status)

        self.state = status

    async def _async_update_data(self) -> None:
        """Fetch data from Meianlike."""
        try:
            async with timeout(10):
                await self.hass.async_add_executor_job(self._update_data)
        except ConnectionError as error:
            raise UpdateFailed(error) from error
