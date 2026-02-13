"""FastMCP Server Definition for Datadog MCP.

This module creates the FastMCP instance with Keycard authentication
and registers all tools. Uses the Keycard SDK for OAuth token management.
"""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from .auth import auth_provider
from .tools.monitors import register_monitor_tools
from .tools.hosts import register_host_tools
from .tools.metrics import register_metric_tools
from .tools.logs import register_log_tools
from .tools.events import register_event_tools
from .tools.dashboards import register_dashboard_tools
from .tools.incidents import register_incident_tools
from .tools.slos import register_slo_tools
from .tools.traces import register_trace_tools

# Load environment variables
load_dotenv()


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server instance.

    Returns:
        Configured FastMCP instance with Keycard auth and all tools registered.
    """
    # Get RemoteAuthProvider from Keycard AuthProvider
    auth = auth_provider.get_remote_auth_provider()

    mcp = FastMCP(
        "Datadog MCP Server",
        auth=auth,
        instructions="""Datadog MCP Server for infrastructure monitoring and observability.

This server provides read-only tools to:
- List and inspect monitors and their alert status
- Search and list hosts in your infrastructure
- Query timeseries metrics and list active metrics
- Search logs with filtering and time ranges
- Browse events from your Datadog event stream
- List and inspect dashboards
- View incidents and their details
- Check SLO status and history
- Search APM traces and spans

All tools are read-only. Authentication is handled via Keycard OAuth.
""",
    )

    # Register tools from separate modules
    register_monitor_tools(mcp)
    register_host_tools(mcp)
    register_metric_tools(mcp)
    register_log_tools(mcp)
    register_event_tools(mcp)
    register_dashboard_tools(mcp)
    register_incident_tools(mcp)
    register_slo_tools(mcp)
    register_trace_tools(mcp)

    return mcp


# Create the server instance
mcp = create_mcp_server()


# For local development and Render deployment
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Datadog MCP Server on http://0.0.0.0:{port}/mcp")

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port
    )
