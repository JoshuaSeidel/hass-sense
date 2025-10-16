"""Sense Coordinators."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

from .const import (
    ACTIVE_UPDATE_RATE,
    TREND_UPDATE_RATE,
    SENSE_TIMEOUT_EXCEPTIONS,
    SENSE_WEBSOCKET_EXCEPTIONS,
    CONF_ELECTRICITY_RATE,
    CONF_SOLAR_CREDIT_RATE,
    DEFAULT_ELECTRICITY_RATE,
    DEFAULT_SOLAR_CREDIT_RATE,
)
from .statistics import SenseAnalytics
from .cost_calculator import CostCalculator

try:
    from sense_energy import (
        ASyncSenseable,
        SenseAuthenticationException,
        SenseMFARequiredException,
    )
except ImportError:
    ASyncSenseable = None
    SenseAuthenticationException = Exception
    SenseMFARequiredException = Exception

_LOGGER = logging.getLogger(__name__)


class SenseCoordinator(DataUpdateCoordinator[None]):
    """Base Sense Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        gateway: ASyncSenseable,
        name: str,
        update_interval: int,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"Sense {name} {gateway.sense_monitor_id}",
            update_interval=timedelta(seconds=update_interval),
        )
        self._gateway = gateway
        self.last_update_success = False


class SenseRealtimeCoordinator(SenseCoordinator):
    """Sense Realtime Coordinator - Fast updates for power data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        gateway: ASyncSenseable,
        update_rate: int = ACTIVE_UPDATE_RATE,
    ) -> None:
        """Initialize."""
        super().__init__(hass, config_entry, gateway, "Realtime", update_rate)
        self.gateway = gateway  # Expose gateway for sensor access
        self.analytics = SenseAnalytics(hass)  # Analytics engine
        
        # Initialize cost calculator with configured rates
        electricity_rate = config_entry.data.get(CONF_ELECTRICITY_RATE, DEFAULT_ELECTRICITY_RATE)
        solar_credit = config_entry.data.get(CONF_SOLAR_CREDIT_RATE, DEFAULT_SOLAR_CREDIT_RATE)
        self.cost_calculator = CostCalculator(hass, electricity_rate, solar_credit)

    async def _async_update_data(self) -> dict:
        """Retrieve latest realtime state and return data dict."""
        try:
            await self._gateway.update_realtime()
            
            active_power = getattr(self._gateway, 'active_power', 0)
            active_solar = getattr(self._gateway, 'active_solar_power', 0)
            
            # Update analytics
            self.analytics.update(active_power, active_solar)
            
            _LOGGER.info(
                "Realtime update (%ss interval): %sW, Solar: %sW",
                self.update_interval.total_seconds(),
                active_power,
                active_solar,
            )
        except SENSE_TIMEOUT_EXCEPTIONS as ex:
            _LOGGER.debug("Timeout retrieving realtime data: %s", ex)
            # Don't fail - WebSocket may just be slow
        except SENSE_WEBSOCKET_EXCEPTIONS as ex:
            _LOGGER.warning("Failed to update realtime data: %s", ex)
            # Don't fail - keep old data
        
        # Build data dict from gateway attributes
        power_stats = self.analytics.power_stats.to_dict()
        solar_stats = self.analytics.solar_stats.to_dict()
        anomaly = self.analytics.detect_anomaly()
        
        return {
            "active_power": getattr(self._gateway, 'active_power', 0),
            "active_solar_power": getattr(self._gateway, 'active_solar_power', 0),
            "voltage": getattr(self._gateway, 'active_voltage', []),
            "hz": getattr(self._gateway, 'hz', 0) or getattr(self._gateway, 'active_frequency', 0),
            "active_devices": [d.name for d in getattr(self._gateway, 'devices', []) if getattr(d, 'state', None) == 'on'],
            "devices": getattr(self._gateway, 'devices', []),
            # Analytics data
            "peak_power": power_stats['max_power'],
            "avg_power": power_stats['avg_power'],
            "power_variance": power_stats['variance'],
            "recent_15min_avg": power_stats['recent_15min_avg'],
            "solar_peak": solar_stats['max_production'],
            "solar_self_consumption": solar_stats['avg_self_consumption'],
            "anomaly_detected": anomaly is not None,
            "anomaly_data": anomaly,
        }


class SenseTrendCoordinator(SenseCoordinator):
    """Sense Trend Coordinator - Slower updates for historical data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        gateway: ASyncSenseable,
    ) -> None:
        """Initialize."""
        super().__init__(hass, config_entry, gateway, "Trends", TREND_UPDATE_RATE)
        self.gateway = gateway  # Expose gateway for sensor access
        
        # Initialize cost calculator with configured rates
        electricity_rate = config_entry.data.get(CONF_ELECTRICITY_RATE, DEFAULT_ELECTRICITY_RATE)
        solar_credit = config_entry.data.get(CONF_SOLAR_CREDIT_RATE, DEFAULT_SOLAR_CREDIT_RATE)
        self.cost_calculator = CostCalculator(hass, electricity_rate, solar_credit)

    async def _async_update_data(self) -> dict:
        """Update the trend data and return data dict."""
        try:
            await self._gateway.update_trend_data()
            _LOGGER.debug(
                "Trend update: Daily %skWh, Monthly %skWh",
                self._gateway.daily_usage,
                self._gateway.monthly_usage,
            )
        except SENSE_TIMEOUT_EXCEPTIONS as ex:
            _LOGGER.debug("Timeout retrieving trend data: %s", ex)
            # Non-critical, keep old data
        except Exception as ex:
            _LOGGER.debug("Failed to update trend data (non-critical): %s", ex)
            # Trend data is non-critical
        
        # Build data dict from gateway attributes
        return {
            "daily_usage": getattr(self._gateway, 'daily_usage', 0),
            "daily_production": getattr(self._gateway, 'daily_production', 0),
            "weekly_usage": getattr(self._gateway, 'weekly_usage', 0),
            "weekly_production": getattr(self._gateway, 'weekly_production', 0),
            "monthly_usage": getattr(self._gateway, 'monthly_usage', 0),
            "monthly_production": getattr(self._gateway, 'monthly_production', 0),
            "yearly_usage": getattr(self._gateway, 'yearly_usage', 0),
            "yearly_production": getattr(self._gateway, 'yearly_production', 0),
        }

