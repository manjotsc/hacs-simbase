"""The Simbase integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SimbaseApiClient
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    SERVICE_ACTIVATE_SIM,
    SERVICE_DEACTIVATE_SIM,
    SERVICE_SEND_SMS,
    ATTR_ICCID,
)
from .coordinator import SimbaseDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Simbase from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_key = entry.data[CONF_API_KEY]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    session = async_get_clientsession(hass)
    api_client = SimbaseApiClient(api_key, session)

    coordinator = SimbaseDataUpdateCoordinator(
        hass,
        entry,
        api_client,
        scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api_client": api_client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await _async_setup_services(hass)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up Simbase services."""

    async def async_activate_sim(call: ServiceCall) -> None:
        """Activate a SIM card."""
        iccid = call.data[ATTR_ICCID]
        for entry_data in hass.data[DOMAIN].values():
            coordinator: SimbaseDataUpdateCoordinator = entry_data["coordinator"]
            if coordinator.get_simcard(iccid):
                await coordinator.async_activate_simcard(iccid)
                return
        _LOGGER.error("SIM card with ICCID %s not found", iccid)

    async def async_deactivate_sim(call: ServiceCall) -> None:
        """Deactivate a SIM card."""
        iccid = call.data[ATTR_ICCID]
        for entry_data in hass.data[DOMAIN].values():
            coordinator: SimbaseDataUpdateCoordinator = entry_data["coordinator"]
            if coordinator.get_simcard(iccid):
                await coordinator.async_deactivate_simcard(iccid)
                return
        _LOGGER.error("SIM card with ICCID %s not found", iccid)

    async def async_send_sms(call: ServiceCall) -> None:
        """Send SMS to a SIM card."""
        iccid = call.data[ATTR_ICCID]
        message = call.data["message"]
        for entry_data in hass.data[DOMAIN].values():
            coordinator: SimbaseDataUpdateCoordinator = entry_data["coordinator"]
            if coordinator.get_simcard(iccid):
                await coordinator.async_send_sms(iccid, message)
                return
        _LOGGER.error("SIM card with ICCID %s not found", iccid)

    # Only register if not already registered
    if not hass.services.has_service(DOMAIN, SERVICE_ACTIVATE_SIM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ACTIVATE_SIM,
            async_activate_sim,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_DEACTIVATE_SIM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_DEACTIVATE_SIM,
            async_deactivate_sim,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_SMS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_SMS,
            async_send_sms,
        )
