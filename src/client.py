"""Datadog API Client.

Provides async HTTP client for making authenticated requests to the Datadog API.
Credentials are provided by the calling tool function from Keycard AccessContext.

Datadog authentication uses DD-API-KEY and DD-APPLICATION-KEY headers
instead of a Bearer token.
"""

from typing import Any

import httpx

DATADOG_API_URL = "https://api.us5.datadoghq.com"


class DatadogClientError(Exception):
    """Raised when Datadog API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def request(
    method: str,
    path: str,
    *,
    api_key: str,
    application_key: str,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make an authenticated request to Datadog API.

    Args:
        method: HTTP method (GET or POST).
        path: API path (e.g., "/api/v1/monitor").
        api_key: Datadog DD-API-KEY.
        application_key: Datadog DD-APPLICATION-KEY.
        params: Optional query parameters.
        json: Optional JSON body (for POST requests).

    Returns:
        Parsed JSON response dict.

    Raises:
        DatadogClientError: If the API returns an error.
    """
    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": application_key,
        "Content-Type": "application/json",
    }

    url = f"{DATADOG_API_URL}{path}"

    # Filter out None values from params
    if params:
        params = {k: v for k, v in params.items() if v is not None}

    # Filter out None values from json body
    if json:
        json = {k: v for k, v in json.items() if v is not None}

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json,
            timeout=30.0,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                errors = error_data.get("errors", [])
                message = "; ".join(errors) if errors else response.text
            except Exception:
                message = response.text
            raise DatadogClientError(
                f"Datadog API error ({response.status_code}): {message}",
                status_code=response.status_code,
            )

        # Some endpoints return empty body (204)
        if response.status_code == 204 or not response.content:
            return {}

        return response.json()
