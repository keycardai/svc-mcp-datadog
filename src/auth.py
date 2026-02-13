"""Keycard Authentication Provider for Datadog MCP Server.

This module creates the AuthProvider singleton that is used by all tool modules.
The auth_provider must be initialized before tools are registered.

Datadog requires two credentials (DD-API-KEY and DD-APPLICATION-KEY) instead
of a single Bearer token. The Keycard integration delivers both through the
token exchange mechanism.
"""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from keycardai.mcp.integrations.fastmcp import AuthProvider, ClientSecret

if TYPE_CHECKING:
    from keycardai.mcp.integrations.fastmcp import AccessContext

# Load environment variables
load_dotenv()

# Datadog API resource URL for grant decorator
DATADOG_API_URL = "https://api.us5.datadoghq.com"

# Create Keycard authentication provider
# This is a module-level singleton used by all tools
auth_provider = AuthProvider(
    zone_id=os.getenv("KEYCARD_ZONE_ID"),
    mcp_server_name="Datadog MCP Server",
    mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/"),
    application_credential=ClientSecret((
        os.getenv("KEYCARD_CLIENT_ID"),
        os.getenv("KEYCARD_CLIENT_SECRET")
    ))
)


@dataclass
class DatadogCredentials:
    """Datadog API credentials extracted from Keycard AccessContext."""
    api_key: str
    application_key: str


def get_datadog_credentials(access_ctx: "AccessContext") -> DatadogCredentials:
    """Extract Datadog API credentials from Keycard AccessContext.

    Args:
        access_ctx: The AccessContext from ctx.get_state("keycardai")

    Returns:
        DatadogCredentials with both api_key and application_key.

    Raises:
        ValueError: If credentials cannot be extracted or auth errors occurred.
    """
    if access_ctx is None:
        raise ValueError("No authentication context - Keycard auth may not be configured")

    if access_ctx.has_errors():
        errors = access_ctx.get_errors()
        raise ValueError(f"Authentication errors: {errors}")

    token_response = access_ctx.access(DATADOG_API_URL)

    api_key = token_response.access_token
    raw = getattr(token_response, "raw", None) or {}
    application_key = raw.get("dd_application_key") or raw.get("application_key")

    if not application_key:
        raise ValueError(
            "DD-APPLICATION-KEY not found in token response. "
            "Ensure the Keycard Datadog integration is configured to provide both keys."
        )

    return DatadogCredentials(api_key=api_key, application_key=application_key)
