"""Binary sensor platform for Sense Energy Monitor."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up Sense binary sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    gateway = hass.data[DOMAIN][config_entry.entry_id]["gateway"]

    # Get all discovered devices
    devices = await gateway.get_discovered_device_data()
    
    entities = [
        SenseDeviceBinarySensor(
            coordinator,
            device,
            gateway.sense_monitor_id,
        )
        for device in devices
    ]

    async_add_entities(entities)


class SenseDeviceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Sense device as a binary sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(
        self,
        coordinator,
        device: dict,
        monitor_id: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device = device
        self._device_id = device.get("id")
        self._device_name = device.get("name", "Unknown Device")
        self._monitor_id = monitor_id
        
        self._attr_unique_id = f"{monitor_id}_device_{self._device_id}"
        self._attr_name = self._device_name
        self._attr_icon = ICON_DEVICE
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, monitor_id)},
            "name": "Sense Energy Monitor",
            "manufacturer": "Sense",
            "model": "Energy Monitor",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the device is on."""
        if self.coordinator.data:
            active_devices = self.coordinator.data.get("active_devices", [])
            return self._device_name in active_devices
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        # Find the device in the current data
        devices = self.coordinator.data.get("devices", [])
        current_device = next(
            (d for d in devices if d.get("id") == self._device_id),
            None
        )
        
        if current_device:
            return {
                "device_id": self._device_id,
                "icon": current_device.get("icon"),
                "tags": current_device.get("tags", []),
                "location": current_device.get("location"),
                "make": current_device.get("make"),
                "model": current_device.get("model"),
            }
        
        return {"device_id": self._device_id}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

