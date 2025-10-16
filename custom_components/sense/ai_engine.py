"""AI-powered energy intelligence for Sense Energy Monitor."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """Configuration for AI features."""
    
    enabled: bool = False
    provider: str = "ha_conversation"  # ha_conversation, openai, anthropic, built_in
    api_key: str | None = None
    model: str | None = None
    token_budget: str = "medium"  # low, medium, high
    features: dict[str, bool] = None
    
    def __post_init__(self):
        """Initialize features if not provided."""
        if self.features is None:
            self.features = {
                "daily_insights": True,
                "anomaly_explanation": True,
                "solar_coach": True,
                "bill_forecast": True,
                "device_identification": False,
                "weekly_story": True,
                "conversational": False,
                "optimization_suggestions": True,
                "comparative_analysis": False,
            }


# Token budget configurations
TOKEN_BUDGETS = {
    "low": {
        "description": "Minimal AI usage (~$1-2/month)",
        "daily_insights": {"enabled": True, "frequency": "daily", "max_tokens": 500},
        "anomaly_explanation": {"enabled": True, "on_demand": True, "max_tokens": 300},
        "solar_coach": {"enabled": False},
        "bill_forecast": {"enabled": True, "frequency": "weekly", "max_tokens": 400},
        "device_identification": {"enabled": False},
        "weekly_story": {"enabled": True, "frequency": "weekly", "max_tokens": 600},
        "conversational": {"enabled": False},
        "optimization_suggestions": {"enabled": True, "frequency": "weekly", "max_tokens": 500},
        "comparative_analysis": {"enabled": False},
    },
    "medium": {
        "description": "Balanced AI usage (~$3-5/month)",
        "daily_insights": {"enabled": True, "frequency": "daily", "max_tokens": 800},
        "anomaly_explanation": {"enabled": True, "on_demand": True, "max_tokens": 500},
        "solar_coach": {"enabled": True, "frequency": "hourly", "max_tokens": 200},
        "bill_forecast": {"enabled": True, "frequency": "weekly", "max_tokens": 600},
        "device_identification": {"enabled": True, "on_demand": True, "max_tokens": 400},
        "weekly_story": {"enabled": True, "frequency": "weekly", "max_tokens": 1000},
        "conversational": {"enabled": True, "max_tokens": 500},
        "optimization_suggestions": {"enabled": True, "frequency": "weekly", "max_tokens": 800},
        "comparative_analysis": {"enabled": False},
    },
    "high": {
        "description": "Full AI features (~$8-12/month)",
        "daily_insights": {"enabled": True, "frequency": "daily", "max_tokens": 1500},
        "anomaly_explanation": {"enabled": True, "on_demand": True, "max_tokens": 800},
        "solar_coach": {"enabled": True, "frequency": "realtime", "max_tokens": 300},
        "bill_forecast": {"enabled": True, "frequency": "daily", "max_tokens": 1000},
        "device_identification": {"enabled": True, "on_demand": True, "max_tokens": 600},
        "weekly_story": {"enabled": True, "frequency": "weekly", "max_tokens": 2000},
        "conversational": {"enabled": True, "max_tokens": 1000},
        "optimization_suggestions": {"enabled": True, "frequency": "daily", "max_tokens": 1200},
        "comparative_analysis": {"enabled": True, "frequency": "monthly", "max_tokens": 1000},
    },
}


class SenseAIEngine:
    """AI engine for energy intelligence."""
    
    def __init__(self, hass: HomeAssistant, config: AIConfig):
        """Initialize AI engine."""
        self.hass = hass
        self.config = config
        self._cache = {}
        self._last_calls = {}
    
    async def call_llm(
        self,
        prompt: str,
        context: dict[str, Any],
        feature: str,
        max_tokens: int | None = None,
    ) -> str:
        """Call LLM with prompt and context."""
        if not self.config.enabled:
            return "AI features disabled"
        
        # Check rate limiting
        if not self._should_call(feature):
            return self._get_cached_response(feature)
        
        # Build full prompt
        full_prompt = self._build_prompt(prompt, context, feature)
        
        # Determine max tokens
        if max_tokens is None:
            budget = TOKEN_BUDGETS.get(self.config.token_budget, TOKEN_BUDGETS["medium"])
            max_tokens = budget.get(feature, {}).get("max_tokens", 500)
        
        try:
            # Call appropriate LLM provider
            if self.config.provider == "ha_conversation":
                response = await self._call_ha_conversation(full_prompt)
            elif self.config.provider == "openai":
                response = await self._call_openai(full_prompt, max_tokens)
            elif self.config.provider == "anthropic":
                response = await self._call_anthropic(full_prompt, max_tokens)
            elif self.config.provider == "built_in":
                response = await self._call_built_in(full_prompt, context, feature)
            else:
                response = "Unknown AI provider"
            
            # Cache response
            self._cache[feature] = {
                "response": response,
                "timestamp": datetime.now(),
                "context": context,
            }
            self._last_calls[feature] = datetime.now()
            
            return response
            
        except Exception as ex:
            _LOGGER.error("Error calling LLM for %s: %s", feature, ex)
            return f"Error generating AI response: {ex}"
    
    async def _call_ha_conversation(self, prompt: str) -> str:
        """Call Home Assistant conversation integration."""
        try:
            response = await self.hass.services.async_call(
                "conversation",
                "process",
                {"text": prompt},
                blocking=True,
                return_response=True,
            )
            return response.get("response", {}).get("speech", {}).get("plain", {}).get("speech", "No response")
        except Exception as ex:
            _LOGGER.error("Error calling HA conversation: %s", ex)
            raise
    
    async def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """Call OpenAI API directly."""
        try:
            # Use HA's OpenAI integration if available
            response = await self.hass.services.async_call(
                "openai_conversation",
                "generate_response",
                {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                },
                blocking=True,
                return_response=True,
            )
            return response.get("text", "No response")
        except Exception as ex:
            _LOGGER.error("Error calling OpenAI: %s", ex)
            raise
    
    async def _call_anthropic(self, prompt: str, max_tokens: int) -> str:
        """Call Anthropic API directly."""
        try:
            # Use HA's Anthropic integration if available
            response = await self.hass.services.async_call(
                "anthropic",
                "generate_response",
                {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                },
                blocking=True,
                return_response=True,
            )
            return response.get("text", "No response")
        except Exception as ex:
            _LOGGER.error("Error calling Anthropic: %s", ex)
            # Fallback to conversation
            return await self._call_ha_conversation(prompt)
    
    async def _call_built_in(self, prompt: str, context: dict, feature: str) -> str:
        """Built-in rule-based responses (fallback)."""
        # Simple rule-based responses for when no LLM is available
        if feature == "daily_insights":
            return self._generate_basic_insights(context)
        elif feature == "anomaly_explanation":
            return self._generate_basic_anomaly_explanation(context)
        elif feature == "solar_coach":
            return self._generate_basic_solar_advice(context)
        else:
            return "AI feature requires LLM provider configuration"
    
    def _build_prompt(self, prompt: str, context: dict, feature: str) -> str:
        """Build complete prompt with context."""
        system_context = """You are an expert energy analyst helping homeowners understand and optimize their electricity usage. 
Provide clear, actionable insights in a friendly, conversational tone. Focus on practical recommendations that save money and energy.
Be specific with numbers and percentages. Keep responses concise but informative."""
        
        context_str = json.dumps(context, indent=2, default=str)
        
        return f"""{system_context}

Context Data:
{context_str}

Task: {prompt}

Please provide a helpful, specific response based on the data above."""
    
    def _should_call(self, feature: str) -> bool:
        """Check if we should make an LLM call based on rate limiting."""
        budget = TOKEN_BUDGETS.get(self.config.token_budget, TOKEN_BUDGETS["medium"])
        feature_config = budget.get(feature, {})
        
        if not feature_config.get("enabled", False):
            return False
        
        # On-demand features always allowed
        if feature_config.get("on_demand", False):
            return True
        
        # Check frequency
        frequency = feature_config.get("frequency", "daily")
        last_call = self._last_calls.get(feature)
        
        if last_call is None:
            return True
        
        now = datetime.now()
        if frequency == "realtime":
            return (now - last_call) > timedelta(minutes=5)
        elif frequency == "hourly":
            return (now - last_call) > timedelta(hours=1)
        elif frequency == "daily":
            return (now - last_call) > timedelta(days=1)
        elif frequency == "weekly":
            return (now - last_call) > timedelta(days=7)
        elif frequency == "monthly":
            return (now - last_call) > timedelta(days=30)
        
        return False
    
    def _get_cached_response(self, feature: str) -> str:
        """Get cached response if available."""
        cached = self._cache.get(feature)
        if cached:
            return cached["response"]
        return "No cached response available"
    
    def _generate_basic_insights(self, context: dict) -> str:
        """Generate basic insights without LLM."""
        usage = context.get("daily_usage", 0)
        cost = context.get("daily_cost", 0)
        peak = context.get("peak_power", 0)
        
        return f"Today's usage: {usage:.1f} kWh (${cost:.2f}). Peak power: {peak:.0f}W. Enable AI features for detailed insights and recommendations."
    
    def _generate_basic_anomaly_explanation(self, context: dict) -> str:
        """Generate basic anomaly explanation without LLM."""
        current = context.get("current_power", 0)
        expected = context.get("expected_power", 0)
        deviation = context.get("deviation", 0)
        
        return f"Power usage ({current:.0f}W) is {deviation:.1f}x higher than expected ({expected:.0f}W). Check for running appliances or devices."
    
    def _generate_basic_solar_advice(self, context: dict) -> str:
        """Generate basic solar advice without LLM."""
        production = context.get("solar_production", 0)
        usage = context.get("current_usage", 0)
        excess = production - usage
        
        if excess > 500:
            return f"Good time to run appliances! {excess:.0f}W excess solar available."
        elif excess > 0:
            return f"Solar producing {production:.0f}W, using {usage:.0f}W. Slight excess available."
        else:
            return f"Drawing {abs(excess):.0f}W from grid. Solar: {production:.0f}W"
    
    def get_privacy_info(self) -> dict:
        """Get information about what data is sent to LLM."""
        return {
            "data_sent": [
                "Energy usage statistics (kWh, watts)",
                "Peak power times and values",
                "Device names and states (if enabled)",
                "Solar production data (if applicable)",
                "Cost calculations (no personal financial info)",
                "Time-of-day patterns",
                "Historical trends (aggregated)",
            ],
            "data_not_sent": [
                "Your name or address",
                "Account numbers or payment info",
                "Specific device locations in home",
                "Real-time video or images",
                "Personal schedules or calendar",
                "Other smart home device data",
            ],
            "provider": self.config.provider,
            "retention": "Responses cached locally, not stored by provider (per their policies)",
            "opt_out": "Disable AI features anytime in integration options",
        }
    
    def get_cost_estimate(self) -> dict:
        """Estimate monthly AI costs based on token budget."""
        budget = TOKEN_BUDGETS.get(self.config.token_budget, TOKEN_BUDGETS["medium"])
        
        # Rough cost estimates (varies by provider)
        cost_per_1k_tokens = {
            "ha_conversation": 0.0,  # Free if using local LLM
            "openai": 0.002,  # GPT-4 Turbo input
            "anthropic": 0.003,  # Claude 3 Sonnet
            "built_in": 0.0,
        }
        
        base_cost = cost_per_1k_tokens.get(self.config.provider, 0.002)
        
        # Calculate monthly token usage
        monthly_tokens = 0
        for feature, config in budget.items():
            if not config.get("enabled", False):
                continue
            
            max_tokens = config.get("max_tokens", 500)
            frequency = config.get("frequency", "daily")
            
            if frequency == "realtime":
                calls_per_month = 30 * 24 * 12  # Every 5 min
            elif frequency == "hourly":
                calls_per_month = 30 * 24
            elif frequency == "daily":
                calls_per_month = 30
            elif frequency == "weekly":
                calls_per_month = 4
            elif frequency == "monthly":
                calls_per_month = 1
            else:
                calls_per_month = 0
            
            monthly_tokens += max_tokens * calls_per_month
        
        estimated_cost = (monthly_tokens / 1000) * base_cost
        
        return {
            "budget_level": self.config.token_budget,
            "description": budget.get("description", ""),
            "estimated_monthly_tokens": monthly_tokens,
            "estimated_monthly_cost": round(estimated_cost, 2),
            "provider": self.config.provider,
            "note": "Actual costs may vary based on usage and provider pricing",
        }

