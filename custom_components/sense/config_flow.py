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
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_TIMEOUT,
    SENSE_TIMEOUT_EXCEPTIONS,
    SENSE_WEBSOCKET_EXCEPTIONS,
    CONF_REALTIME_UPDATE_RATE,
    CONF_ELECTRICITY_RATE,
    CONF_SOLAR_CREDIT_RATE,
    CONF_CURRENCY,
    ACTIVE_UPDATE_RATE,
    UPDATE_RATE_OPTIONS,
    DEFAULT_ELECTRICITY_RATE,
    DEFAULT_SOLAR_CREDIT_RATE,
    DEFAULT_CURRENCY,
    CURRENCY_OPTIONS,
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

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Don't set self.config_entry - it's inherited from parent
        # But we need to accept it in __init__
        super().__init__()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Enable AI if provider is selected (not "none")
            ai_provider = user_input.get("ai_provider", "none")
            user_input["ai_enabled"] = ai_provider != "none"
            
            # Convert realtime_update_rate back to int
            if CONF_REALTIME_UPDATE_RATE in user_input:
                user_input[CONF_REALTIME_UPDATE_RATE] = int(user_input[CONF_REALTIME_UPDATE_RATE])
            
            # Update the config entry with new options
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data={})

        current_rate = self.config_entry.data.get(
            CONF_REALTIME_UPDATE_RATE, ACTIVE_UPDATE_RATE
        )
        
        electricity_rate = self.config_entry.data.get(
            CONF_ELECTRICITY_RATE, DEFAULT_ELECTRICITY_RATE
        )
        solar_credit_rate = self.config_entry.data.get(
            CONF_SOLAR_CREDIT_RATE, DEFAULT_SOLAR_CREDIT_RATE
        )
        currency = self.config_entry.data.get(
            CONF_CURRENCY, DEFAULT_CURRENCY
        )
        
        ai_provider = self.config_entry.data.get("ai_provider", "none")
        ai_agent_id = self.config_entry.data.get("ai_agent_id", "")
        ai_token_budget = self.config_entry.data.get("ai_token_budget", "medium")
        
        # Check which integrations are available
        provider_options = {
            "none": "Disabled",
            "ha_conversation": "Home Assistant Conversation (Free)",
        }
        
        # Check if OpenAI conversation is available
        if "openai_conversation" in self.hass.config.components:
            provider_options["openai"] = "OpenAI Conversation"
        
        # Check if Anthropic conversation is available
        if any(domain in self.hass.config.components for domain in ["anthropic", "anthropic_conversation"]):
            provider_options["anthropic"] = "Anthropic Conversation"
        
        # Build schema dynamically based on AI provider selection  
        # Convert UPDATE_RATE_OPTIONS to proper selector format
        update_rate_options_list = []
        for k, v in UPDATE_RATE_OPTIONS.items():
            update_rate_options_list.append(
                selector.SelectOptionDict(value=str(k), label=v)
            )
        
        provider_options_list = []
        for k, v in provider_options.items():
            provider_options_list.append(
                selector.SelectOptionDict(value=k, label=v)
            )
        
        currency_options_list = []
        for k, v in CURRENCY_OPTIONS.items():
            currency_options_list.append(
                selector.SelectOptionDict(value=k, label=v)
            )
        
        schema_dict = {
            vol.Required(
                CONF_REALTIME_UPDATE_RATE,
                default=str(current_rate),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=update_rate_options_list,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_ELECTRICITY_RATE,
                default=electricity_rate,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.01,
                    max=1.0,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_SOLAR_CREDIT_RATE,
                default=solar_credit_rate,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CURRENCY,
                default=currency,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=currency_options_list,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                "ai_provider",
                default=ai_provider,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=provider_options_list,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
        
        # Show agent_id dropdown if OpenAI or Anthropic selected
        if ai_provider in ["openai", "anthropic"]:
            # Get list of conversation agents
            agent_options_list = [
                selector.SelectOptionDict(value="", label="Auto-detect (Recommended)")
            ]
            
            # Find all conversation agents
            conversation_entities = self.hass.states.async_all("conversation")
            for entity in conversation_entities:
                agent_id = entity.entity_id
                # Get friendly name or use entity_id
                friendly_name = entity.attributes.get("friendly_name", agent_id)
                agent_options_list.append(
                    selector.SelectOptionDict(value=agent_id, label=friendly_name)
                )
            
            # If no agents found, add some common ones
            if len(agent_options_list) == 1:
                agent_options_list.extend([
                    selector.SelectOptionDict(value="conversation.openai", label="OpenAI (conversation.openai)"),
                    selector.SelectOptionDict(value="conversation.gpt_4o", label="GPT-4o (conversation.gpt_4o)"),
                    selector.SelectOptionDict(value="conversation.gpt_4o_mini", label="GPT-4o Mini (conversation.gpt_4o_mini)"),
                    selector.SelectOptionDict(value="conversation.anthropic", label="Anthropic (conversation.anthropic)"),
                ])
            
            schema_dict[vol.Optional(
                "ai_agent_id",
                default=ai_agent_id if ai_agent_id else "",
            )] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=agent_options_list,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        
        # Only show token budget if AI is enabled
        if ai_provider != "none":
            token_budget_options_list = [
                selector.SelectOptionDict(value="low", label="Low - Essential features (~10K tokens/month)"),
                selector.SelectOptionDict(value="medium", label="Medium - Recommended (~30K tokens/month)"),
                selector.SelectOptionDict(value="high", label="High - All features (~75K tokens/month)"),
            ]
            
            schema_dict[vol.Required(
                "ai_token_budget",
                default=ai_token_budget,
            )] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=token_budget_options_list,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "info": "Configure update rate and AI features."
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

