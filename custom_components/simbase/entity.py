"""Base entity for Simbase integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SimbaseDataUpdateCoordinator


class SimbaseEntity(CoordinatorEntity[SimbaseDataUpdateCoordinator]):
    """Base class for Simbase entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SimbaseDataUpdateCoordinator,
        iccid: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._iccid = iccid
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, iccid)},
            name=self._get_sim_name(),
            manufacturer="Simbase",
            model="IoT SIM",
            sw_version=self._get_sim_data().get("firmware_version"),
            configuration_url="https://dashboard.simbase.com",
        )

    def _get_sim_data(self) -> dict:
        """Get the SIM card data."""
        return self.coordinator.get_simcard(self._iccid) or {}

    def _get_sim_name(self) -> str:
        """Get the SIM card name."""
        sim_data = self._get_sim_data()
        name = sim_data.get("name") or sim_data.get("label")
        if name:
            return name
        # Use last 4 digits of ICCID as fallback
        return f"SIM ...{self._iccid[-4:]}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self._get_sim_data() is not None


class SimbaseAccountEntity(CoordinatorEntity[SimbaseDataUpdateCoordinator]):
    """Base class for Simbase account-level entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SimbaseDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the account entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"account_{entry_id}")},
            name="Simbase Account",
            manufacturer="Simbase",
            model="Account",
            configuration_url="https://dashboard.simbase.com",
        )

    def _get_account_data(self) -> dict:
        """Get the account data."""
        return self.coordinator.get_account_data() or {}

    def _get_balance_data(self) -> dict:
        """Get the balance data."""
        return self.coordinator.get_balance() or {}

    def _get_totals(self) -> dict:
        """Get the calculated totals."""
        return self.coordinator.get_totals() or {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
