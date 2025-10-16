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
from .ai_engine import SenseAIEngine, AIConfig
from .ai_features import (
    DailyInsightsGenerator,
    AnomalyExplainer,
    SolarCoach,
    BillForecaster,
    DeviceIdentifier,
    WeeklyStoryteller,
    OptimizationSuggester,
    ConversationalAssistant,
    ComparativeAnalyzer,
)

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
    # Check if already set up (shouldn't happen, but be defensive)
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        _LOGGER.warning("Sense entry %s already set up, skipping", entry.entry_id)
        return True
    
    entry_data = entry.data
    email = entry_data[CONF_EMAIL]
    password = entry_data[CONF_PASSWORD]
    timeout = entry_data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    
    # Get user-configured update rate early (needed for rate limiting)
    realtime_update_rate = entry_data.get(CONF_REALTIME_UPDATE_RATE, ACTIVE_UPDATE_RATE)

    client_session = async_get_clientsession(hass)

    if USE_OFFICIAL_LIB:
        _LOGGER.info("Using official sense_energy library with %ss update rate", realtime_update_rate)
        
        # Creating ASyncSenseable does blocking I/O (SSL certs)
        gateway = await hass.async_add_executor_job(
            partial(
                ASyncSenseable,
                api_timeout=timeout,
                wss_timeout=timeout,
                client_session=client_session,
            )
        )
        # Set rate limit to user's chosen update rate
        gateway.rate_limit = realtime_update_rate
        
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

    # Initialize AI features if enabled
    ai_config = AIConfig(
        enabled=entry_data.get("ai_enabled", False),
        provider=entry_data.get("ai_provider", "ha_conversation"),
        agent_id=entry_data.get("ai_agent_id"),
        token_budget=entry_data.get("ai_token_budget", "medium"),
    )
    
    ai_engine = None
    ai_features = {}
    
    if ai_config.enabled:
        _LOGGER.info("Initializing AI features with provider: %s, budget: %s", 
                     ai_config.provider, ai_config.token_budget)
        ai_engine = SenseAIEngine(hass, ai_config)
        
        # Initialize all AI feature generators
        ai_features = {
            "daily_insights": DailyInsightsGenerator(ai_engine),
            "anomaly_explainer": AnomalyExplainer(ai_engine),
            "solar_coach": SolarCoach(ai_engine),
            "bill_forecast": BillForecaster(ai_engine),
            "device_identifier": DeviceIdentifier(ai_engine),
            "weekly_story": WeeklyStoryteller(ai_engine),
            "optimization": OptimizationSuggester(ai_engine),
            "conversational": ConversationalAssistant(ai_engine),
            "comparative": ComparativeAnalyzer(ai_engine),
        }

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "realtime_coordinator": realtime_coordinator,
        "trend_coordinator": trend_coordinator,
        "gateway": gateway,
        "ai_config": ai_config,
        "ai_engine": ai_engine,
        "ai_features": ai_features,
        # Keep old key for backwards compatibility with sensors
        "coordinator": realtime_coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass, gateway)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options when they change."""
    _LOGGER.info("Options changed, reloading Sense integration")
    # Reload the entire integration to apply new settings
    await hass.config_entries.async_reload(entry.entry_id)


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
    
    # Register AI services if enabled
    for entry_id, data in hass.data[DOMAIN].items():
        ai_config = data.get("ai_config")
        if ai_config and ai_config.enabled:
            await async_setup_ai_services(hass, data)
            break  # Only register once


async def async_setup_ai_services(hass: HomeAssistant, data: dict) -> None:
    """Set up AI-powered services."""
    ai_engine = data["ai_engine"]
    ai_features = data["ai_features"]
    realtime_coordinator = data["realtime_coordinator"]
    trend_coordinator = data["trend_coordinator"]
    
    async def handle_ask_ai(call: ServiceCall) -> dict:
        """Handle ask_ai service."""
        question = call.data.get("question")
        
        realtime_data = realtime_coordinator.data or {}
        trend_data = trend_coordinator.data or {}
        
        context_data = {
            "current_power": realtime_data.get("active_power", 0),
            "daily_usage": trend_data.get("daily_usage", 0),
            "monthly_usage": trend_data.get("monthly_usage", 0),
            "active_devices": realtime_data.get("active_devices", []),
        }
        
        result = await ai_features["conversational"].answer(question, context_data)
        
        # Fire event with response
        hass.bus.async_fire(
            f"{DOMAIN}_ai_response",
            {"question": question, "answer": result.get("answer")}
        )
        
        return result
    
    async def handle_identify_device(call: ServiceCall) -> dict:
        """Handle identify_device service."""
        device_id = call.data.get("device_id")
        
        # Get device data
        device_data = {
            "id": device_id,
            "avg_power": 1500,  # TODO: Get from actual device data
            "duration": 90,
        }
        
        result = await ai_features["device_identifier"].identify(device_data)
        
        hass.bus.async_fire(
            f"{DOMAIN}_device_identified",
            {"device_id": device_id, "identification": result.get("identification")}
        )
        
        return result
    
    async def handle_explain_anomaly(call: ServiceCall) -> dict:
        """Handle explain_anomaly service."""
        realtime_data = realtime_coordinator.data or {}
        
        if not realtime_data.get("anomaly_detected", False):
            return {"explanation": "No anomaly currently detected"}
        
        anomaly_data = realtime_data.get("anomaly_data", {})
        device_data = {
            "active_devices": realtime_data.get("active_devices", []),
        }
        
        result = await ai_features["anomaly_explainer"].explain(anomaly_data, device_data)
        
        hass.bus.async_fire(
            f"{DOMAIN}_anomaly_explained",
            {"explanation": result.get("explanation")}
        )
        
        return result
    
    async def handle_generate_insights(call: ServiceCall) -> dict:
        """Handle generate_insights service."""
        period = call.data.get("period", "daily")
        
        realtime_data = realtime_coordinator.data or {}
        trend_data = trend_coordinator.data or {}
        
        if period == "daily":
            data = {
                "daily_usage": trend_data.get("daily_usage", 0),
                "peak_power": realtime_data.get("peak_power", 0),
            }
            result = await ai_features["daily_insights"].generate(data)
        elif period == "weekly":
            data = {
                "weekly_usage": trend_data.get("weekly_usage", 0),
            }
            result = await ai_features["weekly_story"].tell_story(data)
        else:
            result = {"error": "Invalid period"}
        
        return result
    
    async def handle_generate_optimization(call: ServiceCall) -> dict:
        """Handle generate_optimization service."""
        result = await ai_features["optimization"].suggest({})
        return result
    
    async def handle_get_privacy_info(call: ServiceCall) -> dict:
        """Handle get_privacy_info service."""
        return ai_engine.get_privacy_info()
    
    async def handle_get_cost_estimate(call: ServiceCall) -> dict:
        """Handle get_cost_estimate service."""
        return ai_engine.get_cost_estimate()
    
    # Register all AI services
    hass.services.async_register(
        DOMAIN, "ask_ai", handle_ask_ai, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "identify_device", handle_identify_device, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "explain_anomaly", handle_explain_anomaly, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "generate_insights", handle_generate_insights, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "generate_optimization", handle_generate_optimization, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "get_privacy_info", handle_get_privacy_info, supports_response="optional"
    )
    hass.services.async_register(
        DOMAIN, "get_cost_estimate", handle_get_cost_estimate, supports_response="optional"
    )
    
    _LOGGER.info("AI services registered")

