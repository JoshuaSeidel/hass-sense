"""Cost calculation utilities for Sense Energy Monitor."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Default electricity rates (USD per kWh)
DEFAULT_RATE = 0.12
DEFAULT_SOLAR_CREDIT = 0.10


class CostCalculator:
    """Calculate energy costs and savings."""

    def __init__(
        self,
        hass: HomeAssistant,
        energy_rate: float = DEFAULT_RATE,
        solar_credit: float = DEFAULT_SOLAR_CREDIT,
        distribution_rate: float = 0.0,
        time_of_use: dict | None = None,
    ) -> None:
        """Initialize cost calculator.
        
        Args:
            hass: Home Assistant instance
            energy_rate: Cost per kWh for consumption (generation/supply charge)
            solar_credit: Credit per kWh for solar production
            distribution_rate: Distribution/delivery/transmission charges per kWh
            time_of_use: Optional TOU rate structure:
                {
                    "peak": {"rate": 0.20, "hours": [(16, 21)]},
                    "off_peak": {"rate": 0.08, "hours": [(0, 6), (22, 24)]},
                    "standard": {"rate": 0.12}  # default for other hours
                }
        
        NOTE: Calculated costs do NOT include taxes, regulatory fees, 
        fixed monthly charges, or utility-specific credits. They represent
        the variable energy charges only.
        """
        self.hass = hass
        self.energy_rate = energy_rate
        self.distribution_rate = distribution_rate
        self.solar_credit = solar_credit
        self.time_of_use = time_of_use or {}
    
    @property
    def total_rate(self) -> float:
        """Get total rate (energy + distribution)."""
        return self.energy_rate + self.distribution_rate

    def get_current_rate(self) -> float:
        """Get current energy rate based on time of use (includes distribution)."""
        if not self.time_of_use:
            return self.total_rate

        now = datetime.now()
        current_hour = now.hour

        # Check TOU periods
        for period, config in self.time_of_use.items():
            if "hours" not in config:
                continue
            
            for start_hour, end_hour in config["hours"]:
                if start_hour <= current_hour < end_hour:
                    # TOU rate + distribution
                    return config.get("rate", self.energy_rate) + self.distribution_rate

        # Return standard rate + distribution if no TOU period matches
        return self.time_of_use.get("standard", {}).get("rate", self.energy_rate) + self.distribution_rate

    def calculate_instantaneous_cost(self, power_w: float) -> float:
        """Calculate instantaneous cost per hour at current power draw.
        
        Args:
            power_w: Current power consumption in watts
            
        Returns:
            Cost per hour in dollars
        """
        power_kw = power_w / 1000.0
        rate = self.get_current_rate()
        return power_kw * rate

    def calculate_daily_cost(self, daily_usage_kwh: float) -> float:
        """Calculate cost for daily usage.
        
        Args:
            daily_usage_kwh: Total daily energy usage in kWh
            
        Returns:
            Total cost in dollars
        """
        # For daily totals, use average rate
        if self.time_of_use:
            # Weighted average of TOU rates
            total_hours = 0
            weighted_rate = 0.0
            
            for period, config in self.time_of_use.items():
                if "hours" not in config:
                    continue
                period_hours = sum(
                    end - start for start, end in config["hours"]
                )
                total_hours += period_hours
                weighted_rate += config.get("rate", self.energy_rate) * period_hours
            
            if total_hours > 0:
                rate = weighted_rate / total_hours
            else:
                rate = self.energy_rate
        else:
            rate = self.energy_rate

        return daily_usage_kwh * rate

    def calculate_solar_savings(self, solar_production_kwh: float) -> float:
        """Calculate savings from solar production.
        
        Args:
            solar_production_kwh: Solar energy produced in kWh
            
        Returns:
            Savings in dollars
        """
        return solar_production_kwh * self.solar_credit

    def calculate_net_cost(
        self,
        usage_kwh: float,
        production_kwh: float = 0.0,
    ) -> float:
        """Calculate net cost (usage - solar savings).
        
        Args:
            usage_kwh: Energy consumption in kWh
            production_kwh: Solar production in kWh
            
        Returns:
            Net cost in dollars
        """
        usage_cost = self.calculate_daily_cost(usage_kwh)
        solar_savings = self.calculate_solar_savings(production_kwh)
        return usage_cost - solar_savings

    def estimate_monthly_bill(
        self,
        daily_usage_kwh: float,
        daily_production_kwh: float = 0.0,
        days_in_month: int = 30,
        fixed_charges: float = 10.0,
    ) -> dict:
        """Estimate monthly bill based on daily averages.
        
        Args:
            daily_usage_kwh: Average daily usage
            daily_production_kwh: Average daily solar production
            days_in_month: Number of days in month
            fixed_charges: Fixed monthly charges (service fees, etc.)
            
        Returns:
            Dictionary with bill breakdown
        """
        monthly_usage = daily_usage_kwh * days_in_month
        monthly_production = daily_production_kwh * days_in_month
        
        usage_cost = self.calculate_daily_cost(daily_usage_kwh) * days_in_month
        solar_savings = self.calculate_solar_savings(monthly_production)
        net_energy_cost = usage_cost - solar_savings
        total_bill = net_energy_cost + fixed_charges

        return {
            "monthly_usage_kwh": monthly_usage,
            "monthly_production_kwh": monthly_production,
            "net_usage_kwh": monthly_usage - monthly_production,
            "usage_cost": usage_cost,
            "solar_savings": solar_savings,
            "net_energy_cost": net_energy_cost,
            "fixed_charges": fixed_charges,
            "estimated_total": total_bill,
            "average_rate": self.energy_rate,
            "current_rate": self.get_current_rate(),
        }

    def calculate_peak_cost(self, peak_power_w: float, duration_hours: float) -> float:
        """Calculate cost of a peak power event.
        
        Args:
            peak_power_w: Peak power in watts
            duration_hours: Duration of peak in hours
            
        Returns:
            Cost in dollars
        """
        energy_kwh = (peak_power_w / 1000.0) * duration_hours
        return energy_kwh * self.get_current_rate()

    def get_cost_rate_info(self) -> dict:
        """Get information about current cost rates.
        
        Returns:
            Dictionary with rate information
        """
        return {
            "base_rate": self.energy_rate,
            "solar_credit": self.solar_credit,
            "current_rate": self.get_current_rate(),
            "has_time_of_use": bool(self.time_of_use),
            "tou_periods": list(self.time_of_use.keys()) if self.time_of_use else [],
        }

