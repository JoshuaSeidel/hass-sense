"""AI-powered energy features for Sense."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .ai_engine import SenseAIEngine

_LOGGER = logging.getLogger(__name__)


class DailyInsightsGenerator:
    """Generate daily energy insights."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize generator."""
        self.ai_engine = ai_engine
    
    async def generate(self, data: dict) -> dict:
        """Generate daily insights."""
        context = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "daily_usage_kwh": data.get("daily_usage", 0),
            "daily_cost": data.get("daily_cost", 0),
            "peak_power_w": data.get("peak_power", 0),
            "peak_time": data.get("peak_time"),
            "avg_power_w": data.get("avg_power", 0),
            "active_devices": data.get("active_devices", []),
            "solar_production_kwh": data.get("daily_production", 0),
            "solar_self_consumption_pct": data.get("solar_self_consumption", 0),
            "yesterday_usage_kwh": data.get("yesterday_usage", 0),
            "weather": data.get("weather", {}),
        }
        
        prompt = """Analyze yesterday's energy usage and provide:
1. A brief summary (2-3 sentences)
2. Top 3 specific, actionable recommendations to save energy/money
3. Notable patterns or concerns
4. Comparison to previous day if significantly different

Be specific with numbers. Focus on practical advice."""
        
        response = await self.ai_engine.call_llm(prompt, context, "daily_insights")
        
        return {
            "summary": response,
            "generated_at": datetime.now().isoformat(),
            "data": context,
        }


class AnomalyExplainer:
    """Explain detected anomalies."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize explainer."""
        self.ai_engine = ai_engine
    
    async def explain(self, anomaly_data: dict, device_data: dict) -> dict:
        """Explain an anomaly."""
        context = {
            "current_power_w": anomaly_data.get("current", 0),
            "expected_power_w": anomaly_data.get("expected", 0),
            "deviation_sigma": anomaly_data.get("deviation", 0),
            "time": datetime.now().strftime("%I:%M %p"),
            "active_devices": device_data.get("active_devices", []),
            "recent_device_changes": device_data.get("recent_changes", []),
            "typical_usage_this_time": anomaly_data.get("typical", 0),
        }
        
        prompt = """An unusual power usage spike was detected. Analyze the data and provide:
1. Most likely cause(s) of the spike
2. Which devices to check first
3. Whether this is concerning or normal
4. Recommended actions

Be specific and practical. If multiple devices are running, explain the combination."""
        
        response = await self.ai_engine.call_llm(prompt, context, "anomaly_explanation")
        
        return {
            "explanation": response,
            "severity": "high" if context["deviation_sigma"] > 4 else "medium",
            "generated_at": datetime.now().isoformat(),
        }


class SolarCoach:
    """Provide real-time solar optimization advice."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize coach."""
        self.ai_engine = ai_engine
    
    async def get_advice(self, solar_data: dict) -> dict:
        """Get solar optimization advice."""
        context = {
            "solar_production_w": solar_data.get("production", 0),
            "current_usage_w": solar_data.get("usage", 0),
            "excess_w": solar_data.get("excess", 0),
            "self_consumption_pct": solar_data.get("self_consumption", 0),
            "time": datetime.now().strftime("%I:%M %p"),
            "forecast_next_2h": solar_data.get("forecast", "unknown"),
            "exportable_devices": solar_data.get("controllable_devices", []),
        }
        
        prompt = """Provide real-time solar optimization advice:
1. Current status (1 sentence)
2. Best action right now (run appliance, wait, etc.)
3. Timing for any recommended actions

Be concise and actionable. Focus on maximizing solar self-consumption."""
        
        response = await self.ai_engine.call_llm(prompt, context, "solar_coach")
        
        return {
            "advice": response,
            "status": "optimal" if context["excess_w"] > 500 else "normal",
            "generated_at": datetime.now().isoformat(),
        }


class BillForecaster:
    """Forecast monthly bills with AI analysis."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize forecaster."""
        self.ai_engine = ai_engine
    
    async def forecast(self, usage_data: dict) -> dict:
        """Forecast monthly bill."""
        context = {
            "days_elapsed": usage_data.get("days_elapsed", 0),
            "days_in_month": usage_data.get("days_in_month", 30),
            "usage_so_far_kwh": usage_data.get("month_usage", 0),
            "cost_so_far": usage_data.get("month_cost", 0),
            "daily_average_kwh": usage_data.get("daily_avg", 0),
            "last_month_total_kwh": usage_data.get("last_month", 0),
            "last_month_cost": usage_data.get("last_month_cost", 0),
            "trend": usage_data.get("trend", "stable"),
            "weather_forecast": usage_data.get("weather_forecast", "normal"),
            "rate_structure": usage_data.get("rates", {}),
        }
        
        prompt = """Forecast this month's electricity bill:
1. Projected total cost with confidence level
2. Comparison to last month ($ and %)
3. Main factors driving the projection
4. Top 3 specific actions to reduce the bill
5. Potential savings from each action

Be specific with dollar amounts and percentages."""
        
        response = await self.ai_engine.call_llm(prompt, context, "bill_forecast")
        
        return {
            "forecast": response,
            "projected_cost": usage_data.get("projected_cost", 0),
            "confidence": "medium",
            "generated_at": datetime.now().isoformat(),
        }


class DeviceIdentifier:
    """Help identify unknown devices."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize identifier."""
        self.ai_engine = ai_engine
    
    async def identify(self, device_data: dict) -> dict:
        """Identify unknown device."""
        context = {
            "device_id": device_data.get("id"),
            "avg_power_w": device_data.get("avg_power", 0),
            "peak_power_w": device_data.get("peak_power", 0),
            "typical_duration_min": device_data.get("duration", 0),
            "usage_pattern": device_data.get("pattern", "unknown"),
            "time_of_day": device_data.get("times", []),
            "frequency": device_data.get("frequency", "unknown"),
            "power_signature": device_data.get("signature", {}),
            "known_devices": device_data.get("known_devices", []),
        }
        
        prompt = """Analyze this unknown device and identify what it likely is:
1. Most likely device type (with confidence %)
2. Reasoning based on power signature and patterns
3. Alternative possibilities
4. How to confirm the identification

Be specific about why you think it's that device."""
        
        response = await self.ai_engine.call_llm(prompt, context, "device_identification")
        
        return {
            "identification": response,
            "generated_at": datetime.now().isoformat(),
        }


class WeeklyStoryteller:
    """Generate weekly energy stories."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize storyteller."""
        self.ai_engine = ai_engine
    
    async def tell_story(self, week_data: dict) -> dict:
        """Generate weekly story."""
        context = {
            "week_start": week_data.get("start_date"),
            "week_end": week_data.get("end_date"),
            "total_usage_kwh": week_data.get("total_usage", 0),
            "total_cost": week_data.get("total_cost", 0),
            "daily_breakdown": week_data.get("daily", []),
            "peak_day": week_data.get("peak_day", {}),
            "low_day": week_data.get("low_day", {}),
            "notable_events": week_data.get("events", []),
            "device_highlights": week_data.get("device_highlights", []),
            "solar_summary": week_data.get("solar", {}),
            "vs_last_week": week_data.get("comparison", {}),
        }
        
        prompt = """Create an engaging narrative about this week's energy usage:
1. Opening summary (what kind of week was it?)
2. Day-by-day highlights and interesting patterns
3. Notable achievements or concerns
4. Comparison to last week
5. Looking ahead: recommendations for next week

Write in a friendly, storytelling style. Make the data interesting and relatable."""
        
        response = await self.ai_engine.call_llm(prompt, context, "weekly_story")
        
        return {
            "story": response,
            "generated_at": datetime.now().isoformat(),
        }


class OptimizationSuggester:
    """Suggest energy optimizations and generate automation code."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize suggester."""
        self.ai_engine = ai_engine
    
    async def suggest(self, usage_data: dict) -> dict:
        """Generate optimization suggestions."""
        context = {
            "usage_patterns": usage_data.get("patterns", {}),
            "peak_times": usage_data.get("peak_times", []),
            "off_peak_opportunities": usage_data.get("off_peak", []),
            "device_schedules": usage_data.get("schedules", {}),
            "rate_structure": usage_data.get("rates", {}),
            "solar_availability": usage_data.get("solar", {}),
            "controllable_devices": usage_data.get("controllable", []),
            "current_automations": usage_data.get("automations", []),
        }
        
        prompt = """Analyze usage patterns and suggest optimizations:
1. Top 3 optimization opportunities (with $ savings estimate)
2. For each, provide:
   - What to change
   - Why it saves money
   - Home Assistant automation YAML code
   - Expected monthly savings

Focus on practical, implementable suggestions. Provide actual working YAML."""
        
        response = await self.ai_engine.call_llm(prompt, context, "optimization_suggestions")
        
        return {
            "suggestions": response,
            "generated_at": datetime.now().isoformat(),
        }


class ConversationalAssistant:
    """Answer questions about energy usage."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize assistant."""
        self.ai_engine = ai_engine
    
    async def answer(self, question: str, context_data: dict) -> dict:
        """Answer a question about energy usage."""
        context = {
            "question": question,
            "current_usage_w": context_data.get("current_power", 0),
            "today_usage_kwh": context_data.get("daily_usage", 0),
            "today_cost": context_data.get("daily_cost", 0),
            "month_usage_kwh": context_data.get("monthly_usage", 0),
            "month_cost": context_data.get("monthly_cost", 0),
            "active_devices": context_data.get("active_devices", []),
            "recent_peaks": context_data.get("peaks", []),
            "solar_data": context_data.get("solar", {}),
            "historical_data": context_data.get("historical", {}),
        }
        
        prompt = f"""Answer this question about the user's energy usage: "{question}"

Use the provided data to give a specific, helpful answer. Include:
1. Direct answer to the question
2. Relevant data/numbers
3. Context or explanation
4. Actionable recommendation if applicable

Be conversational but informative."""
        
        response = await self.ai_engine.call_llm(prompt, context, "conversational")
        
        return {
            "answer": response,
            "question": question,
            "generated_at": datetime.now().isoformat(),
        }


class ComparativeAnalyzer:
    """Compare usage to similar homes."""
    
    def __init__(self, ai_engine: SenseAIEngine):
        """Initialize analyzer."""
        self.ai_engine = ai_engine
    
    async def analyze(self, comparison_data: dict) -> dict:
        """Analyze comparative performance."""
        context = {
            "your_usage_kwh": comparison_data.get("usage", 0),
            "your_cost": comparison_data.get("cost", 0),
            "similar_homes_avg": comparison_data.get("avg_similar", 0),
            "percentile": comparison_data.get("percentile", 50),
            "home_size_sqft": comparison_data.get("size", 0),
            "occupants": comparison_data.get("occupants", 0),
            "has_solar": comparison_data.get("solar", False),
            "has_ev": comparison_data.get("ev", False),
            "climate_zone": comparison_data.get("climate", "unknown"),
            "strong_areas": comparison_data.get("strengths", []),
            "weak_areas": comparison_data.get("weaknesses", []),
        }
        
        prompt = """Compare this home's energy usage to similar homes:
1. Overall performance (better/worse/average)
2. Percentile ranking with context
3. What you're doing well
4. Areas for improvement
5. Specific recommendations based on comparison

Be encouraging but honest. Focus on actionable improvements."""
        
        response = await self.ai_engine.call_llm(prompt, context, "comparative_analysis")
        
        return {
            "analysis": response,
            "percentile": context["percentile"],
            "generated_at": datetime.now().isoformat(),
        }

