"""Async Sense API wrapper for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_URL = "https://api.sense.com/apiservice/api/v1"
WS_URL = "wss://clientrt.sense.com/monitors/%s/realtimefeed"
API_TIMEOUT = 30


class SenseableAsync:
    """Async interface to the Sense Energy Monitor API."""

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int = API_TIMEOUT,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the Senseable API."""
        self.username = username
        self.password = password
        self.timeout = timeout
        self._session = session
        self._close_session = False

        # Authentication
        self.sense_access_token = None
        self.sense_user_id = None
        self.sense_monitor_id = None

        # Real-time data
        self.active_power = 0
        self.active_solar_power = 0
        self.voltage = []
        self.hz = 0
        self.active_devices = []

        # Trend data
        self.daily_usage = 0
        self.daily_production = 0
        self.weekly_usage = 0
        self.weekly_production = 0
        self.monthly_usage = 0
        self.monthly_production = 0
        self.yearly_usage = 0
        self.yearly_production = 0

        # Device data
        self.devices = []

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get the aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._close_session and self._session:
            await self._session.close()
            self._session = None

    async def authenticate(self) -> bool:
        """Authenticate with the Sense API."""
        session = await self._get_session()
        auth_data = {
            "email": self.username,
            "password": self.password,
        }

        try:
            async with asyncio.timeout(self.timeout):
                async with session.post(
                    f"{API_URL}/authenticate",
                    json=auth_data,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    self.sense_access_token = data["access_token"]
                    self.sense_user_id = data["user_id"]
                    self.sense_monitor_id = data["monitors"][0]["id"]

                    _LOGGER.debug("Successfully authenticated with Sense API")
                    return True

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout authenticating with Sense API: %s", err)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error authenticating with Sense API: %s", err)
            raise

    async def _api_call(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API call to Sense."""
        if not self.sense_access_token:
            await self.authenticate()

        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.sense_access_token}",
            "Content-Type": "application/json",
        }

        url = f"{API_URL}/{endpoint}"

        try:
            async with asyncio.timeout(self.timeout):
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    json=data,
                ) as response:
                    response.raise_for_status()
                    return await response.json()

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout calling Sense API: %s", err)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error calling Sense API: %s", err)
            raise

    async def update_realtime(self) -> None:
        """Get real-time power data."""
        data = await self._api_call("GET", f"app/monitors/{self.sense_monitor_id}/status")

        if data:
            self.active_power = data.get("w", 0)
            self.active_solar_power = abs(data.get("solar_w", 0))
            self.voltage = data.get("voltage", [])
            self.hz = data.get("hz", 0)

            # Get active devices
            devices_data = data.get("devices", [])
            self.active_devices = [
                device["name"]
                for device in devices_data
                if device.get("state") == "on"
            ]

            _LOGGER.debug("Updated real-time data: %sW, Solar: %sW", self.active_power, self.active_solar_power)

    async def update_trend_data(self) -> None:
        """Get trend data (daily, weekly, monthly, yearly)."""
        # Get daily stats
        daily_data = await self._api_call(
            "GET",
            f"app/history/trends?monitor_id={self.sense_monitor_id}&scale=DAY"
        )
        if daily_data and "consumption" in daily_data:
            self.daily_usage = daily_data["consumption"].get("total", 0)
            self.daily_production = daily_data.get("production", {}).get("total", 0)

        # Get weekly stats
        weekly_data = await self._api_call(
            "GET",
            f"app/history/trends?monitor_id={self.sense_monitor_id}&scale=WEEK"
        )
        if weekly_data and "consumption" in weekly_data:
            self.weekly_usage = weekly_data["consumption"].get("total", 0)
            self.weekly_production = weekly_data.get("production", {}).get("total", 0)

        # Get monthly stats
        monthly_data = await self._api_call(
            "GET",
            f"app/history/trends?monitor_id={self.sense_monitor_id}&scale=MONTH"
        )
        if monthly_data and "consumption" in monthly_data:
            self.monthly_usage = monthly_data["consumption"].get("total", 0)
            self.monthly_production = monthly_data.get("production", {}).get("total", 0)

        # Get yearly stats
        yearly_data = await self._api_call(
            "GET",
            f"app/history/trends?monitor_id={self.sense_monitor_id}&scale=YEAR"
        )
        if yearly_data and "consumption" in yearly_data:
            self.yearly_usage = yearly_data["consumption"].get("total", 0)
            self.yearly_production = yearly_data.get("production", {}).get("total", 0)

        _LOGGER.debug("Updated trend data")

    async def get_discovered_device_names(self) -> list[str]:
        """Get list of discovered device names."""
        data = await self._api_call("GET", f"app/monitors/{self.sense_monitor_id}/devices")
        
        if data:
            self.devices = data
            return [device["name"] for device in data]
        return []

    async def get_discovered_device_data(self) -> list[dict[str, Any]]:
        """Get detailed data for all discovered devices."""
        data = await self._api_call("GET", f"app/monitors/{self.sense_monitor_id}/devices")
        
        if data:
            self.devices = data
            return data
        return []

    async def get_device_info(self, device_id: str) -> dict[str, Any]:
        """Get detailed info for a specific device."""
        data = await self._api_call("GET", f"monitors/{self.sense_monitor_id}/devices/{device_id}")
        return data

    async def reset_device(self, device_id: str) -> None:
        """Reset a device (remove it from learned devices)."""
        await self._api_call(
            "DELETE",
            f"app/monitors/{self.sense_monitor_id}/devices/{device_id}"
        )

    async def rename_device(self, device_id: str, new_name: str) -> None:
        """Rename a device."""
        await self._api_call(
            "PUT",
            f"app/monitors/{self.sense_monitor_id}/devices/{device_id}",
            data={"name": new_name}
        )

    async def get_monitor_info(self) -> dict[str, Any]:
        """Get monitor information."""
        data = await self._api_call("GET", f"app/monitors/{self.sense_monitor_id}")
        return data

    def get_all_data(self) -> dict[str, Any]:
        """Return all current data."""
        return {
            "active_power": self.active_power,
            "active_solar_power": self.active_solar_power,
            "voltage": self.voltage,
            "hz": self.hz,
            "active_devices": self.active_devices,
            "daily_usage": self.daily_usage,
            "daily_production": self.daily_production,
            "weekly_usage": self.weekly_usage,
            "weekly_production": self.weekly_production,
            "monthly_usage": self.monthly_usage,
            "monthly_production": self.monthly_production,
            "yearly_usage": self.yearly_usage,
            "yearly_production": self.yearly_production,
            "devices": self.devices,
        }

