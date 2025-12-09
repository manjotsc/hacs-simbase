"""Data coordinator for Simbase integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SimbaseApiClient, SimbaseApiError
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SimbaseDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Simbase data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api_client: SimbaseApiClient,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api_client = api_client
        self._simcards: dict[str, dict[str, Any]] = {}
        self._usage: dict[str, dict[str, Any]] = {}
        self._account: dict[str, Any] = {}
        self._balance: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Fetch all SIM cards
            _LOGGER.debug("Fetching SIM cards from Simbase API")
            simcards = await self.api_client.get_all_simcards()
            _LOGGER.debug("Received %d SIM cards", len(simcards))

            # Build simcards dict - handle different response formats
            self._simcards = {}
            for sim in simcards:
                # Try different possible ICCID field names
                iccid = sim.get("iccid") or sim.get("ICCID") or sim.get("id")
                if iccid:
                    self._simcards[iccid] = sim
                    _LOGGER.debug("Added SIM with ICCID: %s, data: %s", iccid, sim)
                else:
                    _LOGGER.warning("SIM card without ICCID found: %s", sim)

            _LOGGER.info("Found %d SIM cards in Simbase account", len(self._simcards))

            # Fetch usage data
            try:
                usage_data = await self.api_client.get_all_usage()
                self._usage = {}
                for u in usage_data:
                    iccid = u.get("iccid") or u.get("ICCID") or u.get("id")
                    if iccid:
                        self._usage[iccid] = u
            except SimbaseApiError as err:
                _LOGGER.warning("Failed to fetch usage data: %s", err)
                # Continue with simcard data even if usage fails

            # Merge usage data into simcards
            for iccid, sim in self._simcards.items():
                if iccid in self._usage:
                    sim["usage"] = self._usage[iccid]

            # Extract network operator from SIM data if available
            # Simbase may include network info in various fields
            for iccid, sim in self._simcards.items():
                # Try to find network operator in various possible fields
                operator = (
                    sim.get("operator")
                    or sim.get("network")
                    or sim.get("carrier")
                    or sim.get("operator_name")
                    or sim.get("network_name")
                    or sim.get("current_operator")
                    or sim.get("last_operator")
                    or sim.get("connected_network")
                )
                if operator:
                    sim["network_operator"] = operator
                # Check for MCC/MNC
                mcc = sim.get("mcc") or sim.get("last_mcc")
                mnc = sim.get("mnc") or sim.get("last_mnc")
                if mcc:
                    sim["mcc"] = mcc
                if mnc:
                    sim["mnc"] = mnc

            # Fetch account data (may not be available)
            try:
                self._account = await self.api_client.get_account()
                _LOGGER.debug("Account data: %s", self._account)
            except SimbaseApiError as err:
                _LOGGER.debug("Failed to fetch account data: %s", err)
                self._account = {}

            # Fetch balance data
            try:
                self._balance = await self.api_client.get_balance()
                _LOGGER.debug("Balance data: %s", self._balance)
            except SimbaseApiError as err:
                _LOGGER.debug("Failed to fetch balance data: %s", err)
                self._balance = {}

            # Calculate totals from SIM data
            total_data_usage = 0
            total_cost = 0.0
            active_sims = 0
            inactive_sims = 0
            total_sms_sent = 0
            total_sms_received = 0
            for sim in self._simcards.values():
                # Data usage
                current_month = sim.get("current_month_usage", {})
                if isinstance(current_month, dict):
                    data_bytes = current_month.get("data", 0) or 0
                    total_data_usage += data_bytes
                    # SMS counts
                    sms_mo = current_month.get("sms_mo", 0) or 0
                    sms_mt = current_month.get("sms_mt", 0) or 0
                    total_sms_sent += sms_mo
                    total_sms_received += sms_mt
                # Cost
                current_costs = sim.get("current_month_costs", {})
                if isinstance(current_costs, dict):
                    cost = current_costs.get("total")
                    if cost:
                        try:
                            total_cost += float(cost)
                        except (ValueError, TypeError):
                            pass
                # Status
                state = (sim.get("state") or sim.get("status") or "").lower()
                if state in ("enabled", "active"):
                    active_sims += 1
                else:
                    inactive_sims += 1

            return {
                "simcards": self._simcards,
                "usage": self._usage,
                "count": len(self._simcards),
                "account": self._account,
                "balance": self._balance,
                "totals": {
                    "data_usage_bytes": total_data_usage,
                    "data_usage_mb": round(total_data_usage / (1024 * 1024), 2) if total_data_usage else 0,
                    "total_cost": round(total_cost, 2),
                    "active_sims": active_sims,
                    "inactive_sims": inactive_sims,
                    "sms_sent": total_sms_sent,
                    "sms_received": total_sms_received,
                    "sms_total": total_sms_sent + total_sms_received,
                },
            }

        except SimbaseApiError as err:
            _LOGGER.error("Error communicating with Simbase API: %s", err)
            raise UpdateFailed(f"Error communicating with Simbase API: {err}") from err

    def get_simcard(self, iccid: str) -> dict[str, Any] | None:
        """Get a specific SIM card by ICCID."""
        return self._simcards.get(iccid)

    def get_all_simcards(self) -> dict[str, dict[str, Any]]:
        """Get all SIM cards."""
        return self._simcards

    async def async_activate_simcard(self, iccid: str) -> None:
        """Activate a SIM card."""
        await self.api_client.activate_simcard(iccid)
        await self.async_request_refresh()

    async def async_deactivate_simcard(self, iccid: str) -> None:
        """Deactivate a SIM card."""
        await self.api_client.deactivate_simcard(iccid)
        await self.async_request_refresh()

    async def async_send_sms(self, iccid: str, message: str) -> None:
        """Send SMS to a SIM card."""
        await self.api_client.send_sms(iccid, message)

    def get_account_data(self) -> dict[str, Any]:
        """Get account data."""
        return self._account

    def get_balance(self) -> dict[str, Any]:
        """Get balance data."""
        return self._balance

    def get_totals(self) -> dict[str, Any]:
        """Get calculated totals."""
        if self.data:
            return self.data.get("totals", {})
        return {}

    async def async_activate_all_simcards(self) -> list[dict[str, Any]]:
        """Activate all SIM cards."""
        results = await self.api_client.activate_all_simcards()
        await self.async_request_refresh()
        return results

    async def async_deactivate_all_simcards(self) -> list[dict[str, Any]]:
        """Deactivate all SIM cards."""
        results = await self.api_client.deactivate_all_simcards()
        await self.async_request_refresh()
        return results
