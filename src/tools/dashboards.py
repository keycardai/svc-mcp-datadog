"""Dashboard Tools.

Tools for Datadog dashboards: list_dashboards, get_dashboard.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_dashboard_tools(mcp: FastMCP) -> None:
    """Register dashboard tools with the MCP server."""

    @mcp.tool(
        name="list_dashboards",
        description="List all Datadog dashboards. Returns dashboard titles, IDs, and layout types.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def list_dashboards(
        ctx: Context,
        filter_shared: bool | None = None,
        filter_deleted: bool | None = None,
        count: int = 100,
        start: int = 0,
    ) -> dict:
        """List dashboards in the organization.

        Args:
            filter_shared: If True, return only shared dashboards.
            filter_deleted: If True, include recently deleted dashboards.
            count: Number of dashboards to return.
            start: Starting offset for pagination.
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/dashboard",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "filter[shared]": str(filter_shared).lower() if filter_shared is not None else None,
                    "filter[deleted]": str(filter_deleted).lower() if filter_deleted is not None else None,
                    "count": count,
                    "start": start,
                },
            )

            dashboards = [
                {
                    "id": d.get("id"),
                    "title": d.get("title"),
                    "description": d.get("description"),
                    "layout_type": d.get("layout_type"),
                    "url": d.get("url"),
                    "created_at": d.get("created_at"),
                    "modified_at": d.get("modified_at"),
                    "author_handle": d.get("author_handle"),
                }
                for d in data.get("dashboards", [])
            ]
            return {
                "success": True,
                "dashboards": dashboards,
                "count": len(dashboards),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_dashboard",
        description="Get detailed information about a specific Datadog dashboard including its widgets and layout.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def get_dashboard(
        ctx: Context,
        dashboard_id: str,
    ) -> dict:
        """Get details of a specific dashboard.

        Args:
            dashboard_id: The dashboard ID (e.g., "abc-def-ghi").
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                f"/api/v1/dashboard/{dashboard_id}",
                api_key=creds.api_key,
                application_key=creds.application_key,
            )

            # Summarize widgets to keep response manageable
            widgets = [
                {
                    "id": w.get("id"),
                    "type": w.get("definition", {}).get("type"),
                    "title": w.get("definition", {}).get("title"),
                }
                for w in data.get("widgets", [])
            ]

            dashboard = {
                "id": data.get("id"),
                "title": data.get("title"),
                "description": data.get("description"),
                "layout_type": data.get("layout_type"),
                "url": data.get("url"),
                "widgets": widgets,
                "widget_count": len(widgets),
                "template_variables": data.get("template_variables"),
                "created_at": data.get("created_at"),
                "modified_at": data.get("modified_at"),
                "author_handle": data.get("author_handle"),
            }
            return {"success": True, "dashboard": dashboard}
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
