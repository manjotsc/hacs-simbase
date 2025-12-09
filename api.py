"""Simbase API client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientResponseError

from .const import (
    API_BASE_URL,
    API_ENDPOINT_SIMCARDS,
    API_ENDPOINT_USAGE,
    API_ENDPOINT_EVENTS,
    API_ENDPOINT_ACCOUNT,
    API_ENDPOINT_BALANCE,
)

_LOGGER = logging.getLogger(__name__)

class SimbaseApiError(Exception):
    """Base exception for Simbase API errors."""


class SimbaseAuthError(SimbaseApiError):
    """Authentication error."""


class SimbaseRateLimitError(SimbaseApiError):
    """Rate limit exceeded."""


class SimbaseApiClient:
    """Simbase API client."""

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._session = session
        self._own_session = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        return self._session

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        session = await self._get_session()
        url = f"{API_BASE_URL}{endpoint}"

        _LOGGER.debug("Making %s request to %s with params=%s", method, url, params)

        try:
            async with session.request(
                method,
                url,
                headers=self._get_headers(),
                params=params,
                json=json_data,
            ) as response:
                _LOGGER.debug("Response status: %s", response.status)

                if response.status == 401:
                    raise SimbaseAuthError("Invalid API key")
                if response.status == 429:
                    raise SimbaseRateLimitError("API rate limit exceeded")

                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Response data: %s", data)
                return data
        except ClientResponseError as err:
            # Only log as error for non-404 responses (404 may be expected for some endpoints)
            if err.status == 404:
                _LOGGER.debug("API endpoint not found: %s", err)
            else:
                _LOGGER.error("API request failed: %s", err)
            raise SimbaseApiError(f"API request failed: {err}") from err
        except ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            raise SimbaseApiError(f"Connection error: {err}") from err

    async def validate_api_key(self) -> bool:
        """Validate the API key by making a test request."""
        try:
            await self.get_simcards(limit=1)
            return True
        except SimbaseAuthError:
            return False
        except SimbaseApiError:
            # Other errors might still mean the key is valid
            return True

    async def get_simcards(
        self,
        cursor: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get list of SIM cards."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", API_ENDPOINT_SIMCARDS, params=params)

    async def get_all_simcards(self) -> list[dict[str, Any]]:
        """Get all SIM cards with pagination."""
        simcards = []
        cursor = None

        while True:
            response = await self.get_simcards(cursor=cursor)
            _LOGGER.debug(
                "get_all_simcards response keys: %s",
                list(response.keys()) if isinstance(response, dict) else type(response)
            )

            # Handle different response formats
            if isinstance(response, list):
                # Response is directly a list
                simcards.extend(response)
                break
            elif isinstance(response, dict):
                # Response is wrapped in an object - try various keys
                data = (
                    response.get("data")
                    or response.get("simcards")
                    or response.get("items")
                    or response.get("results")
                    or []
                )
                if isinstance(data, list):
                    simcards.extend(data)
                elif isinstance(data, dict):
                    # Single item response
                    simcards.append(data)

                # Check for pagination
                has_more = response.get("has_more", False) or response.get("hasMore", False)
                if not has_more:
                    break

                cursor = (
                    response.get("cursor")
                    or response.get("next_cursor")
                    or response.get("nextCursor")
                )
                if not cursor:
                    break
            else:
                _LOGGER.warning("Unexpected response type: %s", type(response))
                break

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)

        _LOGGER.debug("Total SIM cards fetched: %d", len(simcards))
        return simcards

    async def get_simcard(self, iccid: str) -> dict[str, Any]:
        """Get a specific SIM card by ICCID."""
        return await self._request("GET", f"{API_ENDPOINT_SIMCARDS}/{iccid}")

    async def activate_simcard(self, iccid: str) -> dict[str, Any]:
        """Activate a SIM card."""
        return await self._request(
            "POST",
            f"{API_ENDPOINT_SIMCARDS}/{iccid}/activate",
        )

    async def deactivate_simcard(self, iccid: str) -> dict[str, Any]:
        """Deactivate a SIM card."""
        return await self._request(
            "POST",
            f"{API_ENDPOINT_SIMCARDS}/{iccid}/deactivate",
        )

    async def get_usage(
        self,
        cursor: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get usage data for SIM cards."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", API_ENDPOINT_USAGE, params=params)

    async def get_all_usage(self) -> list[dict[str, Any]]:
        """Get all usage data with pagination."""
        usage_data = []
        cursor = None

        while True:
            response = await self.get_usage(cursor=cursor)
            data = response.get("data", [])
            usage_data.extend(data)

            if not response.get("has_more", False):
                break

            cursor = response.get("cursor")
            if not cursor:
                break

            await asyncio.sleep(0.1)

        return usage_data

    async def get_events(
        self,
        since: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get events."""
        params = {}
        if since:
            params["since"] = since
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", API_ENDPOINT_EVENTS, params=params)

    async def send_sms(self, iccid: str, message: str) -> dict[str, Any]:
        """Send SMS to a SIM card."""
        return await self._request(
            "POST",
            f"{API_ENDPOINT_SIMCARDS}/{iccid}/sms",
            json_data={"message": message},
        )

    async def update_simcard(
        self,
        iccid: str,
        name: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update SIM card details."""
        data = {}
        if name is not None:
            data["name"] = name
        if tags is not None:
            data["tags"] = tags
        return await self._request(
            "PATCH",
            f"{API_ENDPOINT_SIMCARDS}/{iccid}",
            json_data=data,
        )

    async def get_account(self) -> dict[str, Any]:
        """Get account information."""
        try:
            return await self._request("GET", API_ENDPOINT_ACCOUNT)
        except SimbaseApiError:
            # Fallback - return empty dict if endpoint not available
            _LOGGER.debug("Account endpoint not available")
            return {}

    async def get_balance(self) -> dict[str, Any]:
        """Get account balance."""
        try:
            return await self._request("GET", API_ENDPOINT_BALANCE)
        except SimbaseApiError:
            # Try alternate endpoint
            try:
                account = await self.get_account()
                if "balance" in account:
                    return {"balance": account["balance"]}
            except SimbaseApiError:
                pass
            _LOGGER.debug("Balance endpoint not available")
            return {}

    async def activate_all_simcards(self) -> list[dict[str, Any]]:
        """Activate all SIM cards."""
        results = []
        simcards = await self.get_all_simcards()
        for simcard in simcards:
            iccid = simcard.get("iccid")
            state = (simcard.get("state") or simcard.get("status") or "").lower()
            if iccid and state in ("disabled", "inactive"):
                try:
                    result = await self.activate_simcard(iccid)
                    results.append({"iccid": iccid, "success": True, "result": result})
                except SimbaseApiError as err:
                    results.append({"iccid": iccid, "success": False, "error": str(err)})
                await asyncio.sleep(0.1)  # Rate limit protection
        return results

    async def deactivate_all_simcards(self) -> list[dict[str, Any]]:
        """Deactivate all SIM cards."""
        results = []
        simcards = await self.get_all_simcards()
        for simcard in simcards:
            iccid = simcard.get("iccid")
            state = (simcard.get("state") or simcard.get("status") or "").lower()
            if iccid and state in ("enabled", "active"):
                try:
                    result = await self.deactivate_simcard(iccid)
                    results.append({"iccid": iccid, "success": True, "result": result})
                except SimbaseApiError as err:
                    results.append({"iccid": iccid, "success": False, "error": str(err)})
                await asyncio.sleep(0.1)  # Rate limit protection
        return results
