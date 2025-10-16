"""Statistics and analytics for Sense Energy Monitor."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from statistics import mean, stdev
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


@dataclass
class PowerStatistics:
    """Track power statistics over time."""
    
    max_power: float = 0.0
    min_power: float = float('inf')
    avg_power: float = 0.0
    current_power: float = 0.0
    peak_time: datetime | None = None
    readings_count: int = 0
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update(self, power: float) -> None:
        """Update statistics with new power reading."""
        self.current_power = power
        self.readings_count += 1
        self.history.append({'value': power, 'time': datetime.now()})
        
        # Update max
        if power > self.max_power:
            self.max_power = power
            self.peak_time = datetime.now()
        
        # Update min (ignore zero readings)
        if power > 0 and power < self.min_power:
            self.min_power = power
        
        # Update average
        if self.history:
            self.avg_power = mean(h['value'] for h in self.history)
    
    def get_recent_average(self, minutes: int = 15) -> float:
        """Get average power over recent minutes."""
        if not self.history:
            return 0.0
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [h['value'] for h in self.history if h['time'] > cutoff]
        
        return mean(recent) if recent else 0.0
    
    def get_variance(self) -> float:
        """Get variance in power readings."""
        if len(self.history) < 2:
            return 0.0
        
        values = [h['value'] for h in self.history]
        try:
            return stdev(values)
        except Exception:
            return 0.0
    
    def is_spike(self, threshold: float = 2.0) -> bool:
        """Detect if current reading is a spike (> threshold * avg)."""
        if not self.avg_power or self.avg_power == 0:
            return False
        
        return self.current_power > (self.avg_power * threshold)
    
    def reset_daily(self) -> None:
        """Reset daily statistics."""
        self.max_power = self.current_power
        self.min_power = self.current_power
        self.peak_time = None
        self.readings_count = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'max_power': round(self.max_power, 1),
            'min_power': round(self.min_power, 1) if self.min_power != float('inf') else 0,
            'avg_power': round(self.avg_power, 1),
            'current_power': round(self.current_power, 1),
            'peak_time': self.peak_time.isoformat() if self.peak_time else None,
            'variance': round(self.get_variance(), 1),
            'readings_count': self.readings_count,
            'recent_15min_avg': round(self.get_recent_average(15), 1),
        }


@dataclass
class SolarStatistics:
    """Track solar production statistics."""
    
    max_production: float = 0.0
    total_production_today: float = 0.0
    peak_time: datetime | None = None
    self_consumption_readings: list = field(default_factory=list)
    
    def update(self, production: float, consumption: float) -> None:
        """Update solar statistics."""
        # Update peak production
        if production > self.max_production:
            self.max_production = production
            self.peak_time = datetime.now()
        
        # Track self-consumption rate
        if production > 0:
            self_consumed = min(consumption, production)
            rate = (self_consumed / production) * 100
            self.self_consumption_readings.append(rate)
            
            # Keep only last 100 readings
            if len(self.self_consumption_readings) > 100:
                self.self_consumption_readings = self.self_consumption_readings[-100:]
    
    def get_avg_self_consumption(self) -> float:
        """Get average self-consumption rate."""
        if not self.self_consumption_readings:
            return 0.0
        return mean(self.self_consumption_readings)
    
    def reset_daily(self) -> None:
        """Reset daily statistics."""
        self.max_production = 0.0
        self.peak_time = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'max_production': round(self.max_production, 1),
            'peak_time': self.peak_time.isoformat() if self.peak_time else None,
            'avg_self_consumption': round(self.get_avg_self_consumption(), 1),
            'total_production_today': round(self.total_production_today, 2),
        }


class SenseAnalytics:
    """Analytics engine for Sense data."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize analytics."""
        self.hass = hass
        self.power_stats = PowerStatistics()
        self.solar_stats = SolarStatistics()
        self._last_reset = datetime.now().date()
    
    def update(self, power: float, solar: float = 0.0) -> None:
        """Update analytics with new readings."""
        # Check if we need to reset daily stats
        today = datetime.now().date()
        if today > self._last_reset:
            self.reset_daily()
            self._last_reset = today
        
        # Update statistics
        self.power_stats.update(power)
        if solar > 0:
            self.solar_stats.update(solar, power)
    
    def reset_daily(self) -> None:
        """Reset daily statistics."""
        _LOGGER.info("Resetting daily statistics")
        self.power_stats.reset_daily()
        self.solar_stats.reset_daily()
    
    def get_insights(self) -> dict:
        """Get analytical insights."""
        insights = []
        
        # High usage insight
        if self.power_stats.is_spike(1.5):
            insights.append({
                'type': 'high_usage',
                'message': f"Current usage ({self.power_stats.current_power}W) is significantly higher than average ({self.power_stats.avg_power}W)",
                'severity': 'warning',
            })
        
        # Peak usage insight
        if self.power_stats.max_power > 0:
            insights.append({
                'type': 'peak_usage',
                'message': f"Peak usage today: {self.power_stats.max_power}W at {self.power_stats.peak_time.strftime('%I:%M %p') if self.power_stats.peak_time else 'unknown'}",
                'severity': 'info',
            })
        
        # Solar efficiency insight
        if self.solar_stats.self_consumption_readings:
            avg_consumption = self.solar_stats.get_avg_self_consumption()
            if avg_consumption < 50:
                insights.append({
                    'type': 'solar_efficiency',
                    'message': f"Low solar self-consumption ({avg_consumption:.0f}%). Consider running appliances during sunny hours.",
                    'severity': 'info',
                })
            elif avg_consumption > 90:
                insights.append({
                    'type': 'solar_efficiency',
                    'message': f"Excellent solar self-consumption ({avg_consumption:.0f}%)! You're maximizing your solar investment.",
                    'severity': 'success',
                })
        
        return {
            'insights': insights,
            'power_stats': self.power_stats.to_dict(),
            'solar_stats': self.solar_stats.to_dict(),
        }
    
    def detect_anomaly(self) -> dict | None:
        """Detect anomalous power usage."""
        # Need at least 10 readings for meaningful detection
        if len(self.power_stats.history) < 10:
            return None
        
        # Check if current reading is significantly different from recent average
        recent_avg = self.power_stats.get_recent_average(15)
        variance = self.power_stats.get_variance()
        
        if variance > 0:
            current = self.power_stats.current_power
            deviation = abs(current - recent_avg) / variance
            
            if deviation > 3:  # 3 standard deviations
                return {
                    'detected': True,
                    'current': current,
                    'expected': recent_avg,
                    'deviation': deviation,
                    'message': f"Unusual power usage detected: {current}W (expected ~{recent_avg}W)",
                }
        
        return None

