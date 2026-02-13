"""Pytest configuration and fixtures for Datadog MCP Server tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import FastMCP


@pytest.fixture
def mock_access_ctx():
    """Create a mock AccessContext that returns valid Datadog credentials."""
    access_ctx = MagicMock()
    access_ctx.has_errors.return_value = False

    token_result = MagicMock()
    token_result.access_token = "test-dd-api-key"
    token_result.raw = {"dd_application_key": "test-dd-app-key"}
    access_ctx.access.return_value = token_result

    return access_ctx


@pytest.fixture
def mock_context(mock_access_ctx):
    """Create a mock MCP Context with Keycard state."""
    ctx = MagicMock()
    ctx.get_state.return_value = mock_access_ctx
    return ctx


@pytest.fixture
def mcp_server():
    """Create a test FastMCP server instance."""
    mcp = FastMCP("Test Datadog MCP Server")
    return mcp


@pytest.fixture
def mock_datadog_request():
    """Fixture to mock Datadog API requests."""
    with patch("src.client.request", new_callable=AsyncMock) as mock:
        yield mock
