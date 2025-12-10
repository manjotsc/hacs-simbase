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
    BooleanSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
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
    SENSOR_DATA_USAGE,
    SENSOR_STATUS,
    SENSOR_PLAN,
    SENSOR_MONTHLY_COST,
    SENSOR_SMS_COUNT,
    SENSOR_SMS_SENT,
    SENSOR_SMS_RECEIVED,
    SENSOR_HARDWARE,
    SENSOR_ICCID,
    SENSOR_IMEI,
    SENSOR_MSISDN,
    SENSOR_IP_ADDRESS,
    BINARY_SENSOR_ONLINE,
)

_LOGGER = logging.getLogger(__name__)


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
            # Convert individual toggles back to lists for storage
            enabled_sensors = [
                key for key in AVAILABLE_SENSORS
                if user_input.get(f"sensor_{key}", key in DEFAULT_SENSORS)
            ]
            enabled_binary = [
                key for key in AVAILABLE_BINARY_SENSORS
                if user_input.get(f"binary_{key}", key in DEFAULT_BINARY_SENSORS)
            ]

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
                    CONF_ENABLE_SENSORS: enabled_sensors,
                    CONF_ENABLE_BINARY_SENSORS: enabled_binary,
                    CONF_ENABLE_SWITCH: user_input.get(CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH),
                },
            )

        # Build schema with individual toggles - modern HA style
        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(
                {
                    # Usage & Cost
                    vol.Required(
                        f"sensor_{SENSOR_DATA_USAGE}",
                        default=SENSOR_DATA_USAGE in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_MONTHLY_COST}",
                        default=SENSOR_MONTHLY_COST in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Status
                    vol.Required(
                        f"sensor_{SENSOR_STATUS}",
                        default=SENSOR_STATUS in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_PLAN}",
                        default=SENSOR_PLAN in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"binary_{BINARY_SENSOR_ONLINE}",
                        default=BINARY_SENSOR_ONLINE in DEFAULT_BINARY_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Messaging
                    vol.Required(
                        f"sensor_{SENSOR_SMS_COUNT}",
                        default=SENSOR_SMS_COUNT in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_SMS_SENT}",
                        default=SENSOR_SMS_SENT in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_SMS_RECEIVED}",
                        default=SENSOR_SMS_RECEIVED in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Identifiers
                    vol.Required(
                        f"sensor_{SENSOR_ICCID}",
                        default=SENSOR_ICCID in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_IMEI}",
                        default=SENSOR_IMEI in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_MSISDN}",
                        default=SENSOR_MSISDN in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_IP_ADDRESS}",
                        default=SENSOR_IP_ADDRESS in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Device
                    vol.Required(
                        f"sensor_{SENSOR_HARDWARE}",
                        default=SENSOR_HARDWARE in DEFAULT_SENSORS,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Controls
                    vol.Required(
                        CONF_ENABLE_SWITCH,
                        default=DEFAULT_ENABLE_SWITCH,
                    ): BooleanSelector(BooleanSelectorConfig()),
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
            # Convert individual toggles back to lists for storage
            enabled_sensors = [
                key for key in AVAILABLE_SENSORS
                if user_input.get(f"sensor_{key}", False)
            ]
            enabled_binary = [
                key for key in AVAILABLE_BINARY_SENSORS
                if user_input.get(f"binary_{key}", False)
            ]

            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    CONF_ENABLE_SENSORS: enabled_sensors,
                    CONF_ENABLE_BINARY_SENSORS: enabled_binary,
                    CONF_ENABLE_SWITCH: user_input.get(CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH),
                },
            )

        # Get current settings
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
                    # Update Interval
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
                            mode=NumberSelectorMode.SLIDER,
                            unit_of_measurement="seconds",
                        )
                    ),
                    # Usage & Cost
                    vol.Required(
                        f"sensor_{SENSOR_DATA_USAGE}",
                        default=SENSOR_DATA_USAGE in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_MONTHLY_COST}",
                        default=SENSOR_MONTHLY_COST in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Status
                    vol.Required(
                        f"sensor_{SENSOR_STATUS}",
                        default=SENSOR_STATUS in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_PLAN}",
                        default=SENSOR_PLAN in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"binary_{BINARY_SENSOR_ONLINE}",
                        default=BINARY_SENSOR_ONLINE in current_binary_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Messaging
                    vol.Required(
                        f"sensor_{SENSOR_SMS_COUNT}",
                        default=SENSOR_SMS_COUNT in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_SMS_SENT}",
                        default=SENSOR_SMS_SENT in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_SMS_RECEIVED}",
                        default=SENSOR_SMS_RECEIVED in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Identifiers
                    vol.Required(
                        f"sensor_{SENSOR_ICCID}",
                        default=SENSOR_ICCID in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_IMEI}",
                        default=SENSOR_IMEI in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_MSISDN}",
                        default=SENSOR_MSISDN in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    vol.Required(
                        f"sensor_{SENSOR_IP_ADDRESS}",
                        default=SENSOR_IP_ADDRESS in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Device
                    vol.Required(
                        f"sensor_{SENSOR_HARDWARE}",
                        default=SENSOR_HARDWARE in current_sensors,
                    ): BooleanSelector(BooleanSelectorConfig()),
                    # Controls
                    vol.Required(
                        CONF_ENABLE_SWITCH,
                        default=current_switch,
                    ): BooleanSelector(BooleanSelectorConfig()),
                }
            ),
        )
