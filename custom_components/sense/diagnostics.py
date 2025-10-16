"""Diagnostics support for Sense Energy Monitor."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    gateway = data["gateway"]

    diagnostics_data = {
        "entry": {
            "title": entry.title,
            "unique_id": entry.unique_id,
        },
        "gateway": {
            "monitor_id": gateway.sense_monitor_id,
            "user_id": gateway.sense_user_id,
            "has_access_token": gateway.sense_access_token is not None,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_time": coordinator.last_update_success_time.isoformat()
            if coordinator.last_update_success_time
            else None,
        },
        "data": coordinator.data if coordinator.data else {},
        "gateway_state": {
            "active_power": gateway.active_power,
            "active_solar_power": gateway.active_solar_power,
            "voltage": gateway.voltage,
            "hz": gateway.hz,
            "active_devices": gateway.active_devices,
            "daily_usage": gateway.daily_usage,
            "daily_production": gateway.daily_production,
            "weekly_usage": gateway.weekly_usage,
            "weekly_production": gateway.weekly_production,
            "monthly_usage": gateway.monthly_usage,
            "monthly_production": gateway.monthly_production,
            "yearly_usage": gateway.yearly_usage,
            "yearly_production": gateway.yearly_production,
            "devices_count": len(gateway.devices),
        },
    }

    return diagnostics_data

