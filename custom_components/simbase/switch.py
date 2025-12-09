"""Switch platform for Simbase integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SimbaseApiError
from .const import DOMAIN, CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH
from .coordinator import SimbaseDataUpdateCoordinator
from .entity import SimbaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Simbase switches based on a config entry."""
    # Check if switch is enabled in options
    if not entry.options.get(CONF_ENABLE_SWITCH, DEFAULT_ENABLE_SWITCH):
        return

    coordinator: SimbaseDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[SimbaseActivationSwitch] = []

    for iccid in coordinator.get_all_simcards():
        entities.append(SimbaseActivationSwitch(coordinator, iccid))

    async_add_entities(entities)


class SimbaseActivationSwitch(SimbaseEntity, SwitchEntity):
    """Switch to activate/deactivate a SIM card."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_translation_key = "activation"

    def __init__(
        self,
        coordinator: SimbaseDataUpdateCoordinator,
        iccid: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, iccid)
        self._attr_unique_id = f"{iccid}_activation"

    @property
    def is_on(self) -> bool | None:
        """Return true if the SIM is active/enabled."""
        sim_data = self._get_sim_data()
        status = sim_data.get("status") or sim_data.get("state")
        if status is None:
            return None
        return status.lower() in ("active", "enabled")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        sim_data = self._get_sim_data()
        return {
            "iccid": self._iccid,
            "status": sim_data.get("status") or sim_data.get("state"),
            "activated_at": sim_data.get("activated_at"),
            "suspended_at": sim_data.get("suspended_at"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Activate the SIM card."""
        try:
            await self.coordinator.async_activate_simcard(self._iccid)
        except SimbaseApiError as err:
            _LOGGER.error("Failed to activate SIM %s: %s", self._iccid, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Deactivate the SIM card."""
        try:
            await self.coordinator.async_deactivate_simcard(self._iccid)
        except SimbaseApiError as err:
            _LOGGER.error("Failed to deactivate SIM %s: %s", self._iccid, err)
            raise
