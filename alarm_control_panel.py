"""Interfaces with Meianlike control panels."""
from __future__ import annotations

from pymeianlike import Meianlike

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MeianlikeDataUpdateCoordinator
from .const import DOMAIN

MEIANLIKE_TO_HASS = {
    Meianlike.ARMED_AWAY: STATE_ALARM_ARMED_AWAY,
    Meianlike.ARMED_STAY: STATE_ALARM_ARMED_HOME,
    Meianlike.DISARMED: STATE_ALARM_DISARMED,
    Meianlike.TRIGGERED: STATE_ALARM_TRIGGERED,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a Meianlike alarm control panel based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeianlikePanel(coordinator)])


class MeianlikePanel(
    CoordinatorEntity[MeianlikeDataUpdateCoordinator], AlarmControlPanelEntity
):
    """Representation of an Meianlike device."""

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )
    _attr_name = "Meianlike"
    _attr_icon = "mdi:security"

    def __init__(self, coordinator: MeianlikeDataUpdateCoordinator) -> None:
        """Initialize the alarm panel."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.mac
        self._attr_device_info = DeviceInfo(
            manufacturer="Meianlike",
            name=self.name,
            connections={(device_registry.CONNECTION_NETWORK_MAC, coordinator.mac)},
        )

    @property
    def state(self) -> str | None:
        """Return the state of the device."""
        return MEIANLIKE_TO_HASS.get(self.coordinator.state)

    def alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        self.coordinator.meianlike.disarm()

    def alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        self.coordinator.meianlike.arm_stay()

    def alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        self.coordinator.meianlike.arm_away()
