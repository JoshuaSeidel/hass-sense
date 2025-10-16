"""Sensor platform for Sense Energy Monitor."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfFrequency,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTRIBUTION,
    ICON_POWER,
    ICON_SOLAR,
    ICON_ENERGY,
    ICON_VOLTAGE,
    ICON_FREQUENCY,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SenseSensorEntityDescription(SensorEntityDescription):
    """Describes Sense sensor entity."""

    value_fn: Callable[[dict], StateType] = lambda data: None


SENSOR_TYPES: tuple[SenseSensorEntityDescription, ...] = (
    # Real-time Power Sensors
    SenseSensorEntityDescription(
        key="active_power",
        translation_key="active_power",
        name="Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_POWER,
        value_fn=lambda data: data.get("active_power", 0),
    ),
    SenseSensorEntityDescription(
        key="active_solar_power",
        translation_key="active_solar_power",
        name="Active Solar Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("active_solar_power", 0),
    ),
    # Voltage Sensors
    SenseSensorEntityDescription(
        key="voltage_l1",
        translation_key="voltage_l1",
        name="Voltage L1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_VOLTAGE,
        value_fn=lambda data: data.get("voltage", [])[0] if len(data.get("voltage", [])) > 0 else None,
    ),
    SenseSensorEntityDescription(
        key="voltage_l2",
        translation_key="voltage_l2",
        name="Voltage L2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_VOLTAGE,
        value_fn=lambda data: data.get("voltage", [])[1] if len(data.get("voltage", [])) > 1 else None,
    ),
    # Frequency Sensor
    SenseSensorEntityDescription(
        key="frequency",
        translation_key="frequency",
        name="Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_FREQUENCY,
        value_fn=lambda data: data.get("hz", 0),
    ),
    # Daily Energy Sensors
    SenseSensorEntityDescription(
        key="daily_usage",
        translation_key="daily_usage",
        name="Daily Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_ENERGY,
        value_fn=lambda data: data.get("daily_usage", 0),
    ),
    SenseSensorEntityDescription(
        key="daily_production",
        translation_key="daily_production",
        name="Daily Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("daily_production", 0),
    ),
    # Weekly Energy Sensors
    SenseSensorEntityDescription(
        key="weekly_usage",
        translation_key="weekly_usage",
        name="Weekly Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_ENERGY,
        value_fn=lambda data: data.get("weekly_usage", 0),
    ),
    SenseSensorEntityDescription(
        key="weekly_production",
        translation_key="weekly_production",
        name="Weekly Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("weekly_production", 0),
    ),
    # Monthly Energy Sensors
    SenseSensorEntityDescription(
        key="monthly_usage",
        translation_key="monthly_usage",
        name="Monthly Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_ENERGY,
        value_fn=lambda data: data.get("monthly_usage", 0),
    ),
    SenseSensorEntityDescription(
        key="monthly_production",
        translation_key="monthly_production",
        name="Monthly Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("monthly_production", 0),
    ),
    # Yearly Energy Sensors
    SenseSensorEntityDescription(
        key="yearly_usage",
        translation_key="yearly_usage",
        name="Yearly Usage",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_ENERGY,
        value_fn=lambda data: data.get("yearly_usage", 0),
    ),
    SenseSensorEntityDescription(
        key="yearly_production",
        translation_key="yearly_production",
        name="Yearly Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("yearly_production", 0),
    ),
    # Analytics Sensors
    SenseSensorEntityDescription(
        key="peak_power",
        translation_key="peak_power",
        name="Peak Power Today",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_POWER,
        value_fn=lambda data: data.get("peak_power", 0),
    ),
    SenseSensorEntityDescription(
        key="avg_power",
        translation_key="avg_power",
        name="Average Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_POWER,
        value_fn=lambda data: data.get("avg_power", 0),
    ),
    SenseSensorEntityDescription(
        key="recent_15min_avg",
        translation_key="recent_15min_avg",
        name="15-Minute Average Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_POWER,
        value_fn=lambda data: data.get("recent_15min_avg", 0),
    ),
    SenseSensorEntityDescription(
        key="solar_peak",
        translation_key="solar_peak",
        name="Peak Solar Production Today",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("solar_peak", 0),
    ),
    SenseSensorEntityDescription(
        key="solar_self_consumption",
        translation_key="solar_self_consumption",
        name="Solar Self-Consumption Rate",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_SOLAR,
        value_fn=lambda data: data.get("solar_self_consumption", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sense sensors based on a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    realtime_coordinator = data["realtime_coordinator"]
    trend_coordinator = data["trend_coordinator"]
    gateway = data["gateway"]

    # Determine which coordinator to use for each sensor
    # Realtime sensors: power, voltage, frequency, analytics (fast updates)
    # Trend sensors: daily/weekly/monthly/yearly usage/production (slow updates)
    realtime_keys = {
        "active_power", "active_solar_power", 
        "voltage_l1", "voltage_l2", 
        "frequency",
        # Analytics sensors
        "peak_power", "avg_power", "recent_15min_avg",
        "solar_peak", "solar_self_consumption",
    }

    # Add sensors with appropriate coordinator
    entities = [
        SenseSensor(
            realtime_coordinator if description.key in realtime_keys else trend_coordinator,
            description,
            gateway.sense_monitor_id
        )
        for description in SENSOR_TYPES
    ]
    
    # Add AI sensors if enabled
    ai_config = data.get("ai_config")
    if ai_config and ai_config.enabled:
        _LOGGER.info("Adding AI sensors")
        from .ai_sensor import (
            SenseDailyInsightsSensor,
            SenseSolarCoachSensor,
            SenseBillForecastSensor,
            SenseWeeklyStorySensor,
            SenseOptimizationSensor,
            SenseComparativeSensor,
            SenseAnomalyExplanationSensor,
        )
        
        ai_features = data.get("ai_features", {})
        
        # Add enabled AI sensors based on features
        if ai_config.features.get("daily_insights", True):
            entities.append(
                SenseDailyInsightsSensor(
                    realtime_coordinator,
                    trend_coordinator,
                    ai_features.get("daily_insights"),
                    gateway.sense_monitor_id,
                )
            )
        
        if ai_config.features.get("solar_coach", True):
            entities.append(
                SenseSolarCoachSensor(
                    realtime_coordinator,
                    ai_features.get("solar_coach"),
                    gateway.sense_monitor_id,
                )
            )
        
        if ai_config.features.get("bill_forecast", True):
            entities.append(
                SenseBillForecastSensor(
                    trend_coordinator,
                    ai_features.get("bill_forecast"),
                    gateway.sense_monitor_id,
                )
            )
        
        if ai_config.features.get("weekly_story", True):
            entities.append(
                SenseWeeklyStorySensor(
                    trend_coordinator,
                    ai_features.get("weekly_story"),
                    gateway.sense_monitor_id,
                )
            )
        
        if ai_config.features.get("optimization_suggestions", True):
            entities.append(
                SenseOptimizationSensor(
                    realtime_coordinator,
                    ai_features.get("optimization"),
                    gateway.sense_monitor_id,
                )
            )
        
        if ai_config.features.get("comparative_analysis", False):
            entities.append(
                SenseComparativeSensor(
                    trend_coordinator,
                    ai_features.get("comparative"),
                    gateway.sense_monitor_id,
                )
            )
        
        # Always add anomaly explanation if AI enabled
        entities.append(
            SenseAnomalyExplanationSensor(
                realtime_coordinator,
                ai_features.get("anomaly_explainer"),
                gateway.sense_monitor_id,
            )
        )

    async_add_entities(entities)


class SenseSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sense sensor."""

    entity_description: SenseSensorEntityDescription
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator,
        description: SenseSensorEntityDescription,
        monitor_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{monitor_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, monitor_id)},
            "name": "Sense Energy Monitor",
            "manufacturer": "Sense",
            "model": "Energy Monitor",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

