"""AI-powered sensors for Sense Energy Monitor."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from .ai_engine import SenseAIEngine
    from .ai_features import (
        DailyInsightsGenerator,
        SolarCoach,
        BillForecaster,
        WeeklyStoryteller,
        OptimizationSuggester,
        ComparativeAnalyzer,
    )

from .const import DOMAIN, ATTRIBUTION

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AI sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    
    # Check if AI is enabled
    ai_config = data.get("ai_config")
    if not ai_config or not ai_config.enabled:
        _LOGGER.info("AI features disabled, skipping AI sensors")
        return
    
    ai_engine = data["ai_engine"]
    ai_features = data["ai_features"]
    realtime_coordinator = data["realtime_coordinator"]
    trend_coordinator = data["trend_coordinator"]
    gateway = data["gateway"]
    
    entities = []
    
    # Add enabled sensors based on features
    if ai_config.features.get("daily_insights", False):
        entities.append(
            SenseDailyInsightsSensor(
                realtime_coordinator,
                trend_coordinator,
                ai_features["daily_insights"],
                gateway.sense_monitor_id,
            )
        )
    
    if ai_config.features.get("solar_coach", False):
        entities.append(
            SenseSolarCoachSensor(
                realtime_coordinator,
                ai_features["solar_coach"],
                gateway.sense_monitor_id,
            )
        )
    
    if ai_config.features.get("bill_forecast", False):
        entities.append(
            SenseBillForecastSensor(
                trend_coordinator,
                ai_features["bill_forecast"],
                gateway.sense_monitor_id,
            )
        )
    
    if ai_config.features.get("weekly_story", False):
        entities.append(
            SenseWeeklyStorySensor(
                trend_coordinator,
                ai_features["weekly_story"],
                gateway.sense_monitor_id,
            )
        )
    
    if ai_config.features.get("optimization_suggestions", False):
        entities.append(
            SenseOptimizationSensor(
                realtime_coordinator,
                ai_features["optimization"],
                gateway.sense_monitor_id,
            )
        )
    
    if ai_config.features.get("comparative_analysis", False):
        entities.append(
            SenseComparativeSensor(
                trend_coordinator,
                ai_features["comparative"],
                gateway.sense_monitor_id,
            )
        )
    
    # Add anomaly explanation sensor (always if anomaly detection enabled)
    entities.append(
        SenseAnomalyExplanationSensor(
            realtime_coordinator,
            ai_features["anomaly_explainer"],
            gateway.sense_monitor_id,
        )
    )
    
    async_add_entities(entities)


class SenseAISensor(CoordinatorEntity, SensorEntity):
    """Base class for AI sensors."""
    
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:robot"
    
    def __init__(self, coordinator, monitor_id: str, name: str, unique_id: str):
        """Initialize AI sensor."""
        super().__init__(coordinator)
        self._monitor_id = monitor_id
        self._attr_name = name
        self._attr_unique_id = f"{monitor_id}_{unique_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, monitor_id)},
            "name": "Sense Energy Monitor",
            "manufacturer": "Sense",
            "model": "Energy Monitor",
        }
        self._last_update = None
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Trigger initial update
        await self.async_update()
    
    async def async_update(self) -> None:
        """Update the sensor - override in subclasses."""
        pass


class SenseDailyInsightsSensor(SenseAISensor):
    """Sensor for daily AI insights."""
    
    def __init__(self, realtime_coordinator, trend_coordinator, insights_generator: DailyInsightsGenerator, monitor_id: str):
        """Initialize daily insights sensor."""
        super().__init__(realtime_coordinator, monitor_id, "AI Daily Insights", "ai_daily_insights")
        self._trend_coordinator = trend_coordinator
        self._generator = insights_generator
        self._insights = None
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self._insights:
            return "generated"
        return "pending"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._insights:
            return {"status": "waiting for data"}
        
        return {
            "summary": self._insights.get("summary", ""),
            "generated_at": self._insights.get("generated_at", ""),
            "daily_usage": self._insights.get("data", {}).get("daily_usage_kwh", 0),
            "daily_cost": self._insights.get("data", {}).get("daily_cost", 0),
        }
    
    async def async_update(self) -> None:
        """Update insights once per day."""
        now = datetime.now()
        
        # Update once per day at 6 AM
        if self._last_update and (now - self._last_update) < timedelta(hours=23):
            return
        
        if now.hour < 6:  # Wait until morning
            return
        
        # Collect data from coordinators
        realtime_data = self.coordinator.data or {}
        trend_data = self._trend_coordinator.data or {}
        
        data = {
            "daily_usage": trend_data.get("daily_usage", 0),
            "daily_cost": trend_data.get("daily_usage", 0) * 0.12,  # TODO: Get actual rate
            "peak_power": realtime_data.get("peak_power", 0),
            "avg_power": realtime_data.get("avg_power", 0),
            "daily_production": trend_data.get("daily_production", 0),
            "solar_self_consumption": realtime_data.get("solar_self_consumption", 0),
        }
        
        try:
            self._insights = await self._generator.generate(data)
            self._last_update = now
            _LOGGER.info("Generated daily insights")
        except Exception as ex:
            _LOGGER.error("Error generating daily insights: %s", ex)


class SenseSolarCoachSensor(SenseAISensor):
    """Sensor for solar optimization advice."""
    
    def __init__(self, coordinator, coach: SolarCoach, monitor_id: str):
        """Initialize solar coach sensor."""
        super().__init__(coordinator, monitor_id, "AI Solar Coach", "ai_solar_coach")
        self._coach = coach
        self._advice = None
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self._advice:
            return self._advice.get("status", "normal")
        return "initializing"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._advice:
            return {}
        
        return {
            "advice": self._advice.get("advice", ""),
            "generated_at": self._advice.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update advice hourly."""
        now = datetime.now()
        
        # Update every hour
        if self._last_update and (now - self._last_update) < timedelta(hours=1):
            return
        
        realtime_data = self.coordinator.data or {}
        
        solar_data = {
            "production": realtime_data.get("active_solar_power", 0),
            "usage": realtime_data.get("active_power", 0),
            "excess": realtime_data.get("active_solar_power", 0) - realtime_data.get("active_power", 0),
            "self_consumption": realtime_data.get("solar_self_consumption", 0),
        }
        
        try:
            self._advice = await self._coach.get_advice(solar_data)
            self._last_update = now
        except Exception as ex:
            _LOGGER.error("Error getting solar advice: %s", ex)


class SenseBillForecastSensor(SenseAISensor):
    """Sensor for bill forecasting."""
    
    def __init__(self, coordinator, forecaster: BillForecaster, monitor_id: str):
        """Initialize bill forecast sensor."""
        super().__init__(coordinator, monitor_id, "AI Bill Forecast", "ai_bill_forecast")
        self._forecaster = forecaster
        self._forecast = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "$"
    
    @property
    def native_value(self) -> float:
        """Return the forecasted amount."""
        if self._forecast:
            return self._forecast.get("projected_cost", 0)
        return 0
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._forecast:
            return {}
        
        return {
            "forecast": self._forecast.get("forecast", ""),
            "confidence": self._forecast.get("confidence", ""),
            "generated_at": self._forecast.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update forecast weekly."""
        now = datetime.now()
        
        # Update weekly
        if self._last_update and (now - self._last_update) < timedelta(days=7):
            return
        
        trend_data = self.coordinator.data or {}
        
        days_in_month = 30
        day_of_month = now.day
        
        usage_data = {
            "days_elapsed": day_of_month,
            "days_in_month": days_in_month,
            "month_usage": trend_data.get("monthly_usage", 0),
            "month_cost": trend_data.get("monthly_usage", 0) * 0.12,
            "daily_avg": trend_data.get("monthly_usage", 0) / max(day_of_month, 1),
            "projected_cost": (trend_data.get("monthly_usage", 0) / max(day_of_month, 1)) * days_in_month * 0.12,
        }
        
        try:
            self._forecast = await self._forecaster.forecast(usage_data)
            self._last_update = now
        except Exception as ex:
            _LOGGER.error("Error forecasting bill: %s", ex)


class SenseWeeklyStorySensor(SenseAISensor):
    """Sensor for weekly energy story."""
    
    def __init__(self, coordinator, storyteller: WeeklyStoryteller, monitor_id: str):
        """Initialize weekly story sensor."""
        super().__init__(coordinator, monitor_id, "AI Weekly Story", "ai_weekly_story")
        self._storyteller = storyteller
        self._story = None
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self._story:
            return "published"
        return "pending"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._story:
            return {}
        
        return {
            "story": self._story.get("story", ""),
            "generated_at": self._story.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update story weekly."""
        now = datetime.now()
        
        # Update on Sunday
        if self._last_update and (now - self._last_update) < timedelta(days=7):
            return
        
        if now.weekday() != 6:  # Not Sunday
            return
        
        trend_data = self.coordinator.data or {}
        
        week_data = {
            "start_date": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end_date": now.strftime("%Y-%m-%d"),
            "total_usage": trend_data.get("weekly_usage", 0),
            "total_cost": trend_data.get("weekly_usage", 0) * 0.12,
        }
        
        try:
            self._story = await self._storyteller.tell_story(week_data)
            self._last_update = now
        except Exception as ex:
            _LOGGER.error("Error generating weekly story: %s", ex)


class SenseOptimizationSensor(SenseAISensor):
    """Sensor for optimization suggestions."""
    
    def __init__(self, coordinator, suggester: OptimizationSuggester, monitor_id: str):
        """Initialize optimization sensor."""
        super().__init__(coordinator, monitor_id, "AI Optimization Suggestions", "ai_optimization")
        self._suggester = suggester
        self._suggestions = None
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self._suggestions:
            return "available"
        return "generating"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._suggestions:
            return {}
        
        return {
            "suggestions": self._suggestions.get("suggestions", ""),
            "generated_at": self._suggestions.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update suggestions weekly."""
        now = datetime.now()
        
        # Update weekly
        if self._last_update and (now - self._last_update) < timedelta(days=7):
            return
        
        realtime_data = self.coordinator.data or {}
        
        usage_data = {
            "patterns": {},
            "peak_times": [],
            "controllable": [],
        }
        
        try:
            self._suggestions = await self._suggester.suggest(usage_data)
            self._last_update = now
        except Exception as ex:
            _LOGGER.error("Error generating suggestions: %s", ex)


class SenseComparativeSensor(SenseAISensor):
    """Sensor for comparative analysis."""
    
    def __init__(self, coordinator, analyzer: ComparativeAnalyzer, monitor_id: str):
        """Initialize comparative sensor."""
        super().__init__(coordinator, monitor_id, "AI Comparative Analysis", "ai_comparative")
        self._analyzer = analyzer
        self._analysis = None
    
    @property
    def native_value(self) -> int:
        """Return percentile."""
        if self._analysis:
            return self._analysis.get("percentile", 50)
        return 50
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._analysis:
            return {}
        
        return {
            "analysis": self._analysis.get("analysis", ""),
            "generated_at": self._analysis.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update analysis monthly."""
        now = datetime.now()
        
        # Update monthly
        if self._last_update and (now - self._last_update) < timedelta(days=30):
            return
        
        trend_data = self.coordinator.data or {}
        
        comparison_data = {
            "usage": trend_data.get("monthly_usage", 0),
            "cost": trend_data.get("monthly_usage", 0) * 0.12,
            "percentile": 75,  # TODO: Calculate from real data
        }
        
        try:
            self._analysis = await self._analyzer.analyze(comparison_data)
            self._last_update = now
        except Exception as ex:
            _LOGGER.error("Error generating analysis: %s", ex)


class SenseAnomalyExplanationSensor(SenseAISensor):
    """Sensor for anomaly explanations."""
    
    def __init__(self, coordinator, explainer, monitor_id: str):
        """Initialize anomaly explanation sensor."""
        super().__init__(coordinator, monitor_id, "AI Anomaly Explanation", "ai_anomaly_explanation")
        self._explainer = explainer
        self._explanation = None
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self._explanation:
            return self._explanation.get("severity", "none")
        return "none"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes."""
        if not self._explanation:
            return {"explanation": "No anomaly detected"}
        
        return {
            "explanation": self._explanation.get("explanation", ""),
            "severity": self._explanation.get("severity", ""),
            "generated_at": self._explanation.get("generated_at", ""),
        }
    
    async def async_update(self) -> None:
        """Update when anomaly detected."""
        realtime_data = self.coordinator.data or {}
        
        # Only generate if anomaly detected
        if not realtime_data.get("anomaly_detected", False):
            self._explanation = None
            return
        
        anomaly_data = realtime_data.get("anomaly_data", {})
        device_data = {
            "active_devices": realtime_data.get("active_devices", []),
        }
        
        try:
            self._explanation = await self._explainer.explain(anomaly_data, device_data)
        except Exception as ex:
            _LOGGER.error("Error explaining anomaly: %s", ex)

