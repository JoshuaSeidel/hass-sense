"""The Sense Energy Monitor integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from functools import partial

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
    SENSE_CONNECT_EXCEPTIONS,
    DEFAULT_TIMEOUT,
    ACTIVE_UPDATE_RATE,
    TREND_UPDATE_RATE,
    CONF_REALTIME_UPDATE_RATE,
)
from .coordinator import SenseRealtimeCoordinator, SenseTrendCoordinator

_LOGGER = logging.getLogger(__name__)

try:
    from sense_energy import (
        ASyncSenseable,
        SenseAuthenticationException,
        SenseMFARequiredException,
    )
    USE_OFFICIAL_LIB = True
except ImportError:
    from .sense_api import SenseableAsync as ASyncSenseable
    USE_OFFICIAL_LIB = False
    SenseAuthenticationException = Exception
    SenseMFARequiredException = Exception
    _LOGGER.warning("Using fallback sense_api. Install sense_energy for better support.")

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sense from a config entry."""
    entry_data = entry.data
    email = entry_data[CONF_EMAIL]
    password = entry_data[CONF_PASSWORD]
    timeout = entry_data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    client_session = async_get_clientsession(hass)

    if USE_OFFICIAL_LIB:
        _LOGGER.info("Using official sense_energy library")
        
        # Creating ASyncSenseable does blocking I/O (SSL certs)
        gateway = await hass.async_add_executor_job(
            partial(
                ASyncSenseable,
                api_timeout=timeout,
                wss_timeout=timeout,
                client_session=client_session,
            )
        )
        gateway.rate_limit = ACTIVE_UPDATE_RATE
        
        try:
            # Authenticate and get monitor data
            await gateway.authenticate(email, password)
            await gateway.get_monitor_data()
        except (SenseAuthenticationException, SenseMFARequiredException) as err:
            _LOGGER.warning("Sense authentication failed")
            raise ConfigEntryAuthFailed(err) from err
        except SENSE_TIMEOUT_EXCEPTIONS as err:
            raise ConfigEntryNotReady(str(err) or "Timed out during authentication") from err
        except SENSE_CONNECT_EXCEPTIONS as err:
            raise ConfigEntryNotReady(str(err)) from err
        
        try:
            # Fetch devices and initial realtime update
            await gateway.fetch_devices()
            await gateway.update_realtime()
        except SENSE_TIMEOUT_EXCEPTIONS as err:
            raise ConfigEntryNotReady(str(err) or "Timed out during realtime update") from err
        except SENSE_WEBSOCKET_EXCEPTIONS as err:
            raise ConfigEntryNotReady(str(err) or "Error during realtime update") from err
    else:
        _LOGGER.info("Using custom sense_api implementation")
        gateway = ASyncSenseable(email, password, timeout, client_session)
        try:
            await gateway.authenticate()
        except SENSE_TIMEOUT_EXCEPTIONS as err:
            raise ConfigEntryNotReady(
                f"Timeout during authentication: {err}"
            ) from err
        except SENSE_WEBSOCKET_EXCEPTIONS as err:
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err

    # Get user-configured update rate, or use default
    realtime_update_rate = entry_data.get(CONF_REALTIME_UPDATE_RATE, ACTIVE_UPDATE_RATE)
    
    # Create separate coordinators for realtime and trend data
    # This allows different update intervals: realtime (fast) vs trends (slow)
    realtime_coordinator = SenseRealtimeCoordinator(
        hass, entry, gateway, update_rate=realtime_update_rate
    )
    
    _LOGGER.info(
        "Sense coordinators initialized: realtime=%ss, trends=%ss",
        realtime_update_rate, TREND_UPDATE_RATE
    )
    
    trend_coordinator = SenseTrendCoordinator(hass, entry, gateway)

    # Fetch initial data for both coordinators
    await realtime_coordinator.async_config_entry_first_refresh()
    await trend_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "realtime_coordinator": realtime_coordinator,
        "trend_coordinator": trend_coordinator,
        "gateway": gateway,
        # Keep old key for backwards compatibility with sensors
        "coordinator": realtime_coordinator,
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
        # Close gateway if it has a close method (custom implementation)
        if hasattr(gateway, 'close'):
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

