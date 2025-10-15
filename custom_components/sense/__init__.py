"""The Sense Energy Monitor integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_TIMEOUT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SENSE_TIMEOUT_EXCEPTIONS,
    SENSE_WEBSOCKET_EXCEPTIONS,
    DEFAULT_TIMEOUT,
    ACTIVE_UPDATE_RATE,
)
from .sense_api import SenseableAsync

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sense from a config entry."""
    entry_data = entry.data
    email = entry_data[CONF_EMAIL]
    password = entry_data[CONF_PASSWORD]
    timeout = entry_data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    client_session = async_get_clientsession(hass)

    gateway = SenseableAsync(email, password, timeout, client_session)

    try:
        await gateway.authenticate()
    except SENSE_TIMEOUT_EXCEPTIONS as err:
        raise ConfigEntryNotReady(
            f"Timeout during authentication: {err}"
        ) from err
    except SENSE_WEBSOCKET_EXCEPTIONS as err:
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err

    async def async_update_data():
        """Fetch data from Sense."""
        try:
            # Update realtime data (critical)
            await gateway.update_realtime()
            
            # Try to update trend data (non-critical)
            try:
                await gateway.update_trend_data()
            except Exception as trend_err:
                # Log but don't fail if trend data is unavailable
                _LOGGER.debug("Trend data update failed (non-critical): %s", trend_err)
            
            return gateway.get_all_data()
        except SENSE_TIMEOUT_EXCEPTIONS as err:
            raise UpdateFailed(f"Timeout communicating with Sense API: {err}") from err
        except SENSE_WEBSOCKET_EXCEPTIONS as err:
            raise UpdateFailed(f"Error communicating with Sense API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Sense {email}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=ACTIVE_UPDATE_RATE),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "gateway": gateway,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass, gateway)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        gateway = hass.data[DOMAIN][entry.entry_id]["gateway"]
        await gateway.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant, gateway: SenseableAsync) -> None:
    """Set up services for Sense integration."""

    async def handle_get_device_info(call: ServiceCall) -> None:
        """Handle the get_device_info service call."""
        device_id = call.data.get("device_id")
        device_info = await gateway.get_device_info(device_id)
        _LOGGER.info("Device info for %s: %s", device_id, device_info)
        hass.bus.async_fire(
            f"{DOMAIN}_device_info",
            {"device_id": device_id, "info": device_info}
        )

    async def handle_reset_device(call: ServiceCall) -> None:
        """Handle the reset_device service call."""
        device_id = call.data.get("device_id")
        await gateway.reset_device(device_id)
        _LOGGER.info("Reset device: %s", device_id)

    async def handle_rename_device(call: ServiceCall) -> None:
        """Handle the rename_device service call."""
        device_id = call.data.get("device_id")
        new_name = call.data.get("name")
        await gateway.rename_device(device_id, new_name)
        _LOGGER.info("Renamed device %s to %s", device_id, new_name)

    hass.services.async_register(
        DOMAIN, "get_device_info", handle_get_device_info
    )
    hass.services.async_register(
        DOMAIN, "reset_device", handle_reset_device
    )
    hass.services.async_register(
        DOMAIN, "rename_device", handle_rename_device
    )

