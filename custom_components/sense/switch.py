"""Switch platform for Sense Energy Monitor smart plugs."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION, ICON_DEVICE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sense switches based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    gateway = hass.data[DOMAIN][config_entry.entry_id]["gateway"]

    # Get devices from gateway (already fetched)
    # Don't use get_discovered_device_data() - it's broken in the library
    devices = getattr(gateway, 'devices', [])
    
    # Filter for devices that have control capability
    controllable_devices = [
        device for device in devices
        if getattr(device, 'is_controllable', False) or 
           'plug' in getattr(device, 'tags', [])
    ]
    
    entities = [
        SenseDeviceSwitch(
            coordinator,
            device,
            gateway,
            gateway.sense_monitor_id,
        )
        for device in controllable_devices
    ]

    async_add_entities(entities)


class SenseDeviceSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sense controllable device as a switch."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator,
        device: dict,
        gateway,
        monitor_id: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device = device
        self._device_id = device.get("id")
        self._device_name = device.get("name", "Unknown Device")
        self._gateway = gateway
        self._monitor_id = monitor_id
        
        self._attr_unique_id = f"{monitor_id}_switch_{self._device_id}"
        self._attr_name = f"{self._device_name} Switch"
        self._attr_icon = ICON_DEVICE
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{monitor_id}_device_{self._device_id}")},
            "name": self._device_name,
            "manufacturer": device.get("make", "Unknown"),
            "model": device.get("model", "Smart Plug"),
            "via_device": (DOMAIN, monitor_id),
        }

    @property
    def is_on(self) -> bool:
        """Return true if the device is on."""
        if self.coordinator.data:
            active_devices = self.coordinator.data.get("active_devices", [])
            return self._device_name in active_devices
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        try:
            # Note: Sense API may not support direct control of all devices
            # This is a placeholder for smart plug control
            _LOGGER.info("Turning on device: %s", self._device_name)
            # await self._gateway.turn_on_device(self._device_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning on device %s: %s", self._device_name, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        try:
            # Note: Sense API may not support direct control of all devices
            # This is a placeholder for smart plug control
            _LOGGER.info("Turning off device: %s", self._device_name)
            # await self._gateway.turn_off_device(self._device_id)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error turning off device %s: %s", self._device_name, err)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        devices = self.coordinator.data.get("devices", [])
        current_device = next(
            (d for d in devices if d.get("id") == self._device_id),
            None
        )
        
        if current_device:
            return {
                "device_id": self._device_id,
                "location": current_device.get("location"),
                "tags": current_device.get("tags", []),
            }
        
        return {"device_id": self._device_id}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

