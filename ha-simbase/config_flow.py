"""Config flow for Simbase integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import SimbaseApiClient, SimbaseApiError, SimbaseAuthError
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_ENABLE_SENSORS,
    CONF_ENABLE_BINARY_SENSORS,
    CONF_ENABLE_SWITCH,
    AVAILABLE_SENSORS,
    AVAILABLE_BINARY_SENSORS,
    DEFAULT_SENSORS,
    DEFAULT_BINARY_SENSORS,
    DEFAULT_ENABLE_SWITCH,
)

_LOGGER = logging.getLogger(__name__)


def _get_sensor_options() -> list[dict[str, str]]:
    """Get sensor options for selector."""
    return [
        {"value": key, "label": label}
        for key, label in AVAILABLE_SENSORS.items()
    ]


def _get_binary_sensor_options() -> list[dict[str, str]]:
    """Get binary sensor options for selector."""
    return [
        {"value": key, "label": label}
        for key, label in AVAILABLE_BINARY_SENSORS.items()
    ]


class SimbaseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Simbase."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._api_key: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - API key entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]

            # Check if already configured
            await self.async_set_unique_id(api_key[:16])
            self._abort_if_unique_id_configured()

            # Validate the API key
            session = async_get_clientsession(self.hass)
            client = SimbaseApiClient(api_key, session)

            try:
                valid = await client.validate_api_key()
                if valid:
                    self._api_key = api_key
                    return await self.async_step_sensors()
                else:
                    errors["base"] = "invalid_auth"
            except SimbaseAuthError:
                errors["base"] = "invalid_auth"
            except SimbaseApiError as ex:
                _LOGGER.error("Cannot connect to Simbase: %s", ex)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle sensor selection step."""
        if user_input is not None:
            # Get SIM count for title
            title = "Simbase"
            try:
                session = async_get_clientsession(self.hass)
                client = SimbaseApiClient(self._api_key, session)
                simcards = await client.get_all_simcards()
                sim_count = len(simcards)
                title = f"Simbase ({sim_count} SIMs)"
            except Exception as ex:
                _LOGGER.debug("Could not get SIM count: %s", ex)

            return self.async_create_entry(
                title=title,
                data={
                    CONF_API_KEY: self._api_key,
                },
                options={
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    CONF_ENABLE_SENSORS: user_input.get(CONF_ENABLE_SENSORS, DEFAULT_SENSORS),
                    CONF_ENABLE_BINARY_SENSORS: user_input.get(CONF_ENABLE_BINARY_SENSORS, DEFAULT_BINARY_SENSORS),
                    CONF_ENABLE_SWITCH: user_input.get(CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH),
                },
            )

        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENABLE_SENSORS,
                        default=DEFAULT_SENSORS,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=_get_sensor_options(),
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_BINARY_SENSORS,
                        default=DEFAULT_BINARY_SENSORS,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=_get_binary_sensor_options(),
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_SWITCH,
                        default=DEFAULT_ENABLE_SWITCH,
                    ): BooleanSelector(),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SimbaseOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SimbaseOptionsFlowHandler()


class SimbaseOptionsFlowHandler(OptionsFlow):
    """Handle Simbase options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_sensors = self.config_entry.options.get(
            CONF_ENABLE_SENSORS, DEFAULT_SENSORS
        )
        current_binary_sensors = self.config_entry.options.get(
            CONF_ENABLE_BINARY_SENSORS, DEFAULT_BINARY_SENSORS
        )
        current_switch = self.config_entry.options.get(
            CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=60,
                            max=3600,
                            step=60,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="seconds",
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_SENSORS,
                        default=current_sensors,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=_get_sensor_options(),
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_BINARY_SENSORS,
                        default=current_binary_sensors,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=_get_binary_sensor_options(),
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_SWITCH,
                        default=current_switch,
                    ): BooleanSelector(),
                }
            ),
        )
