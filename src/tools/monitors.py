"""Monitor Tools.

Tools for Datadog monitors: list_monitors, get_monitor.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_monitor_tools(mcp: FastMCP) -> None:
    """Register monitor tools with the MCP server."""

    @mcp.tool(
        name="list_monitors",
        description="List Datadog monitors. Filter by name, tags, or monitor type. Returns monitor name, status, type, and query.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def list_monitors(
        ctx: Context,
        name: str | None = None,
        tags: str | None = None,
        monitor_tags: str | None = None,
        page: int = 0,
        page_size: int = 50,
    ) -> dict:
        """List monitors in the organization.

        Args:
            name: Filter monitors by name (substring match).
            tags: Comma-separated scope tags to filter by (e.g., "env:prod,team:backend").
            monitor_tags: Comma-separated monitor tags to filter by.
            page: Page number for pagination (0-indexed).
            page_size: Number of monitors per page (max 1000).
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/monitor",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "name": name,
                    "tags": tags,
                    "monitor_tags": monitor_tags,
                    "page": page,
                    "page_size": page_size,
                },
            )

            monitors = [
                {
                    "id": m.get("id"),
                    "name": m.get("name"),
                    "type": m.get("type"),
                    "query": m.get("query"),
                    "overall_state": m.get("overall_state"),
                    "message": m.get("message"),
                    "tags": m.get("tags"),
                    "created": m.get("created"),
                    "modified": m.get("modified"),
                }
                for m in data
            ]
            return {
                "success": True,
                "monitors": monitors,
                "count": len(monitors),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_monitor",
        description="Get detailed information about a specific Datadog monitor including its query, status, thresholds, and notification settings.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def get_monitor(
        ctx: Context,
        monitor_id: int,
        group_states: str | None = None,
    ) -> dict:
        """Get details of a specific monitor.

        Args:
            monitor_id: The monitor ID.
            group_states: Comma-separated states to filter groups by (e.g., "alert,warn,no data").
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                f"/api/v1/monitor/{monitor_id}",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "group_states": group_states,
                },
            )

            monitor = {
                "id": data.get("id"),
                "name": data.get("name"),
                "type": data.get("type"),
                "query": data.get("query"),
                "overall_state": data.get("overall_state"),
                "message": data.get("message"),
                "tags": data.get("tags"),
                "options": data.get("options"),
                "state": data.get("state"),
                "created": data.get("created"),
                "modified": data.get("modified"),
                "creator": data.get("creator"),
            }
            return {"success": True, "monitor": monitor}
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
