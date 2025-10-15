"""Constants for the Sense Energy Monitor integration."""
from datetime import timedelta
import asyncio
from aiohttp.client_exceptions import ClientError

DOMAIN = "sense"

# Configuration
CONF_MONITOR_ID = "monitor_id"
DEFAULT_TIMEOUT = 30
ACTIVE_UPDATE_RATE = 60  # seconds

# Sense API Exceptions
SENSE_TIMEOUT_EXCEPTIONS = (asyncio.TimeoutError,)
SENSE_WEBSOCKET_EXCEPTIONS = (ClientError, ConnectionError, OSError)

# Sense Data Keys
SENSE_ACTIVE_POWER = "active_power"
SENSE_ACTIVE_SOLAR_POWER = "active_solar_power"
SENSE_ACTIVE_VOLTAGE = "voltage"
SENSE_ACTIVE_FREQUENCY = "hz"
SENSE_ACTIVE_DEVICES = "active_devices"
SENSE_DEVICES = "devices"

# Trend Data Keys
SENSE_DAILY_USAGE = "daily_usage"
SENSE_DAILY_PRODUCTION = "daily_production"
SENSE_WEEKLY_USAGE = "weekly_usage"
SENSE_WEEKLY_PRODUCTION = "weekly_production"
SENSE_MONTHLY_USAGE = "monthly_usage"
SENSE_MONTHLY_PRODUCTION = "monthly_production"
SENSE_YEARLY_USAGE = "yearly_usage"
SENSE_YEARLY_PRODUCTION = "yearly_production"

# Device States
SENSE_DEVICE_UNKNOWN = "unknown"
SENSE_DEVICE_OFF = "off"
SENSE_DEVICE_ON = "on"

# Attribution
ATTRIBUTION = "Data provided by Sense"

# Icons
ICON_POWER = "mdi:flash"
ICON_ENERGY = "mdi:lightning-bolt"
ICON_SOLAR = "mdi:solar-power"
ICON_VOLTAGE = "mdi:sine-wave"
ICON_FREQUENCY = "mdi:sine-wave"
ICON_DEVICE = "mdi:power-plug"
ICON_COST = "mdi:currency-usd"

# Sensor Types
SENSOR_TYPE_POWER = "power"
SENSOR_TYPE_ENERGY = "energy"
SENSOR_TYPE_VOLTAGE = "voltage"
SENSOR_TYPE_FREQUENCY = "frequency"
SENSOR_TYPE_COST = "cost"

# Update Intervals
REALTIME_UPDATE_INTERVAL = timedelta(seconds=60)
TREND_UPDATE_INTERVAL = timedelta(minutes=5)

