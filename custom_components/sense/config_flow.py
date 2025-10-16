"""Config flow for Sense Energy Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_TIMEOUT,
    SENSE_TIMEOUT_EXCEPTIONS,
    SENSE_WEBSOCKET_EXCEPTIONS,
    CONF_REALTIME_UPDATE_RATE,
    ACTIVE_UPDATE_RATE,
    UPDATE_RATE_OPTIONS,
)
from .sense_api import SenseableAsync

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
        vol.Optional(CONF_REALTIME_UPDATE_RATE, default=ACTIVE_UPDATE_RATE): vol.In(
            {int(k): v for k, v in UPDATE_RATE_OPTIONS.items()}
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    email = data[CONF_EMAIL]
    password = data[CONF_PASSWORD]
    timeout = data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    client_session = async_get_clientsession(hass)
    gateway = SenseableAsync(email, password, timeout, client_session)

    try:
        await gateway.authenticate()
    except SENSE_TIMEOUT_EXCEPTIONS as err:
        raise CannotConnect(f"Timeout connecting to Sense: {err}") from err
    except SENSE_WEBSOCKET_EXCEPTIONS as err:
        raise InvalidAuth(f"Authentication failed: {err}") from err
    finally:
        await gateway.close()

    # Return info that you want to store in the config entry.
    return {
        "title": f"Sense ({email})",
        "monitor_id": gateway.sense_monitor_id,
    }


class SenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sense Energy Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SenseOptionsFlow(config_entry)


class SenseOptionsFlow(config_entries.OptionsFlow):
    """Handle Sense options."""

    # config_entry is available as self.config_entry from parent class
    # No need to set it explicitly (deprecated in HA 2025.12)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Enable AI if provider is selected (not "none")
            ai_provider = user_input.get("ai_provider", "none")
            user_input["ai_enabled"] = ai_provider != "none"
            
            # Update the config entry with new options
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data={})

        current_rate = self.config_entry.data.get(
            CONF_REALTIME_UPDATE_RATE, ACTIVE_UPDATE_RATE
        )
        
        ai_provider = self.config_entry.data.get("ai_provider", "none")
        ai_agent_id = self.config_entry.data.get("ai_agent_id", "")
        ai_token_budget = self.config_entry.data.get("ai_token_budget", "medium")
        
        # Check which integrations are available
        provider_options = {
            "none": "Disabled - No AI Features",
            "ha_conversation": "Home Assistant Conversation (Free - Uses your default agent)",
        }
        
        # Check if OpenAI conversation is available
        if "openai_conversation" in self.hass.config.components:
            provider_options["openai"] = "OpenAI Conversation (Requires configuration)"
        
        # Check if Anthropic conversation is available
        # Anthropic conversation integration domain varies, check common ones
        if any(domain in self.hass.config.components for domain in ["anthropic", "anthropic_conversation"]):
            provider_options["anthropic"] = "Anthropic Conversation (Requires configuration)"
        
        # Build schema dynamically based on AI provider selection
        schema_dict = {
            vol.Required(
                CONF_REALTIME_UPDATE_RATE,
                default=current_rate,
            ): vol.In({int(k): v for k, v in UPDATE_RATE_OPTIONS.items()}),
            vol.Required(
                "ai_provider",
                default=ai_provider,
            ): vol.In(provider_options),
        }
        
        # Show agent_id field if OpenAI or Anthropic selected
        if ai_provider in ["openai", "anthropic"]:
            schema_dict[vol.Optional(
                "ai_agent_id",
                default=ai_agent_id,
                description="Conversation Agent ID (e.g., 'conversation.gpt_4o' or leave empty for auto-detect)",
            )] = str
        
        # Only show token budget if AI is enabled
        if ai_provider != "none":
            schema_dict[vol.Required(
                "ai_token_budget",
                default=ai_token_budget,
            )] = vol.In({
                "low": "Low (~$1-2/month) - Essential features only",
                "medium": "Medium (~$3-5/month) - Recommended",
                "high": "High (~$8-12/month) - All features, real-time",
            })
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "info": "Configure update rate and AI features. AI provides intelligent insights, bill forecasting, and recommendations."
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

