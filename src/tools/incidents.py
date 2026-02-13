"""Incident Tools.

Tools for Datadog incidents: list_incidents, get_incident.
"""

from fastmcp import FastMCP, Context

from ..auth import get_datadog_credentials
from ..client import DatadogClientError, request


def register_incident_tools(mcp: FastMCP) -> None:
    """Register incident tools with the MCP server."""

    @mcp.tool(
        name="list_incidents",
        description="List Datadog incidents. Returns incident title, status, severity, and timestamps.",
    )
    async def list_incidents(
        ctx: Context,
        include: str | None = None,
        page_size: int = 25,
        page_offset: int = 0,
    ) -> dict:
        """List incidents in the organization.

        Args:
            include: Comma-separated related resources to include (e.g., "users,attachments").
            page_size: Number of incidents per page (max 100).
            page_offset: Offset for pagination.
        """
        try:
            creds = get_datadog_credentials()

            data = await request(
                "GET",
                "/api/v2/incidents",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "include": include,
                    "page[size]": page_size,
                    "page[offset]": page_offset,
                },
            )

            incidents = [
                {
                    "id": inc.get("id"),
                    "type": inc.get("type"),
                    "title": inc.get("attributes", {}).get("title"),
                    "status": inc.get("attributes", {}).get("status"),
                    "severity": inc.get("attributes", {}).get("severity"),
                    "created": inc.get("attributes", {}).get("created"),
                    "modified": inc.get("attributes", {}).get("modified"),
                    "resolved": inc.get("attributes", {}).get("resolved"),
                    "customer_impact_scope": inc.get("attributes", {}).get("customer_impact_scope"),
                }
                for inc in data.get("data", [])
            ]
            return {
                "success": True,
                "incidents": incidents,
                "count": len(incidents),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_incident",
        description="Get detailed information about a specific Datadog incident including timeline and impact details.",
    )
    async def get_incident(
        ctx: Context,
        incident_id: str,
        include: str | None = None,
    ) -> dict:
        """Get details of a specific incident.

        Args:
            incident_id: The incident ID.
            include: Related resources to include (e.g., "users,attachments").
        """
        try:
            creds = get_datadog_credentials()

            data = await request(
                "GET",
                f"/api/v2/incidents/{incident_id}",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "include": include,
                },
            )

            inc = data.get("data", {})
            attrs = inc.get("attributes", {})
            incident = {
                "id": inc.get("id"),
                "type": inc.get("type"),
                "title": attrs.get("title"),
                "status": attrs.get("status"),
                "severity": attrs.get("severity"),
                "created": attrs.get("created"),
                "modified": attrs.get("modified"),
                "resolved": attrs.get("resolved"),
                "detected": attrs.get("detected"),
                "customer_impact_scope": attrs.get("customer_impact_scope"),
                "customer_impact_start": attrs.get("customer_impact_start"),
                "customer_impact_end": attrs.get("customer_impact_end"),
                "fields": attrs.get("fields"),
                "notification_handles": attrs.get("notification_handles"),
            }
            return {"success": True, "incident": incident}
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
