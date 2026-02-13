"""Keycard Authentication Provider for Datadog MCP Server.

This module creates the AuthProvider singleton for MCP user authentication
and provides Datadog API credentials from environment variables.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from keycardai.mcp.integrations.fastmcp import AuthProvider, ClientSecret

# Load environment variables
load_dotenv()

# Create Keycard authentication provider
# This is a module-level singleton used for MCP server user authentication
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
    """Datadog API credentials."""
    api_key: str
    application_key: str


def get_datadog_credentials() -> DatadogCredentials:
    """Get Datadog API credentials from environment variables.

    Returns:
        DatadogCredentials with both api_key and application_key.

    Raises:
        ValueError: If required environment variables are not set.
    """
    api_key = os.getenv("DD_API_KEY")
    application_key = os.getenv("DD_APPLICATION_KEY")

    if not api_key:
        raise ValueError("DD_API_KEY environment variable is not set")

    if not application_key:
        raise ValueError("DD_APPLICATION_KEY environment variable is not set")

    return DatadogCredentials(api_key=api_key, application_key=application_key)
