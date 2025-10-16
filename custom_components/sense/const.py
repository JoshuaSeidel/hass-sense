"""Constants for the Sense Energy Monitor integration."""
from datetime import timedelta
import socket

try:
    from sense_energy import (
        SenseAPIException,
        SenseAPITimeoutException,
        SenseWebsocketException,
    )
    SENSE_TIMEOUT_EXCEPTIONS = (TimeoutError, SenseAPITimeoutException)
    SENSE_WEBSOCKET_EXCEPTIONS = (socket.gaierror, SenseWebsocketException)
    SENSE_CONNECT_EXCEPTIONS = (
        socket.gaierror,
        TimeoutError,
        SenseAPITimeoutException,
        SenseAPIException,
    )
except ImportError:
    # Fallback if sense_energy not installed
    import asyncio
    from aiohttp.client_exceptions import ClientError
    SENSE_TIMEOUT_EXCEPTIONS = (asyncio.TimeoutError, TimeoutError)
    SENSE_WEBSOCKET_EXCEPTIONS = (ClientError, ConnectionError, OSError, socket.gaierror)
    SENSE_CONNECT_EXCEPTIONS = SENSE_WEBSOCKET_EXCEPTIONS

DOMAIN = "sense"

# Configuration
CONF_MONITOR_ID = "monitor_id"
CONF_REALTIME_UPDATE_RATE = "realtime_update_rate"
DEFAULT_TIMEOUT = 30
ACTIVE_UPDATE_RATE = 60  # seconds - default for realtime updates
TREND_UPDATE_RATE = 300  # 5 minutes - for historical data

# Update rate options (seconds)
UPDATE_RATE_OPTIONS = {
    "5": "5 seconds (Very Fast - High API usage)",
    "10": "10 seconds (Fast)",
    "15": "15 seconds",
    "30": "30 seconds (Balanced)",
    "60": "60 seconds (Default)",
    "120": "2 minutes (Slow)",
    "300": "5 minutes (Very Slow)",
}

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

