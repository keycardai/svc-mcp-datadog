"""Pytest configuration and fixtures for Datadog MCP Server tests."""

import pytest
from unittest.mock import AsyncMock, patch

from fastmcp import FastMCP


@pytest.fixture(autouse=True)
def mock_datadog_env(monkeypatch):
    """Set Datadog credentials as environment variables for all tests."""
    monkeypatch.setenv("DD_API_KEY", "test-dd-api-key")
    monkeypatch.setenv("DD_APPLICATION_KEY", "test-dd-app-key")


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
