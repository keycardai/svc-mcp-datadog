"""SLO Tools.

Tools for Datadog SLOs: list_slos, get_slo, get_slo_history.
"""

from fastmcp import FastMCP, Context

from ..auth import get_datadog_credentials
from ..client import DatadogClientError, request


def register_slo_tools(mcp: FastMCP) -> None:
    """Register SLO tools with the MCP server."""

    @mcp.tool(
        name="list_slos",
        description="List Datadog Service Level Objectives. Filter by name, tags, or SLO type.",
    )
    async def list_slos(
        ctx: Context,
        ids: str | None = None,
        query: str | None = None,
        tags_query: str | None = None,
        metrics_query: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """List SLOs in the organization.

        Args:
            ids: Comma-separated list of SLO IDs to retrieve.
            query: Search query to filter SLOs by name.
            tags_query: Filter SLOs by tags (e.g., "env:prod").
            metrics_query: Filter metric-based SLOs by metric query.
            limit: Number of SLOs to return.
            offset: Offset for pagination.
        """
        try:
            creds = get_datadog_credentials()

            data = await request(
                "GET",
                "/api/v1/slo",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "ids": ids,
                    "query": query,
                    "tags_query": tags_query,
                    "metrics_query": metrics_query,
                    "limit": limit,
                    "offset": offset,
                },
            )

            slos = [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "description": s.get("description"),
                    "type": s.get("type"),
                    "tags": s.get("tags"),
                    "thresholds": s.get("thresholds"),
                    "created_at": s.get("created_at"),
                    "modified_at": s.get("modified_at"),
                }
                for s in data.get("data", [])
            ]
            return {
                "success": True,
                "slos": slos,
                "count": len(slos),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_slo",
        description="Get detailed information about a specific SLO including its targets, thresholds, and current status.",
    )
    async def get_slo(
        ctx: Context,
        slo_id: str,
        with_configured_alert_ids: bool = False,
    ) -> dict:
        """Get details of a specific SLO.

        Args:
            slo_id: The SLO ID.
            with_configured_alert_ids: Include configured alert IDs.
        """
        try:
            creds = get_datadog_credentials()

            data = await request(
                "GET",
                f"/api/v1/slo/{slo_id}",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "with_configured_alert_ids": str(with_configured_alert_ids).lower(),
                },
            )

            slo_data = data.get("data", {})
            slo = {
                "id": slo_data.get("id"),
                "name": slo_data.get("name"),
                "description": slo_data.get("description"),
                "type": slo_data.get("type"),
                "tags": slo_data.get("tags"),
                "thresholds": slo_data.get("thresholds"),
                "query": slo_data.get("query"),
                "groups": slo_data.get("groups"),
                "monitor_ids": slo_data.get("monitor_ids"),
                "created_at": slo_data.get("created_at"),
                "modified_at": slo_data.get("modified_at"),
                "creator": slo_data.get("creator"),
            }
            return {"success": True, "slo": slo}
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_slo_history",
        description="Get the SLO status history over a time period. Shows how the SLO performed over time.",
    )
    async def get_slo_history(
        ctx: Context,
        slo_id: str,
        from_ts: int,
        to_ts: int,
        target: float | None = None,
    ) -> dict:
        """Get SLO history data.

        Args:
            slo_id: The SLO ID.
            from_ts: Start of the time range (Unix epoch seconds).
            to_ts: End of the time range (Unix epoch seconds).
            target: Target SLO percentage to evaluate against.
        """
        try:
            creds = get_datadog_credentials()

            data = await request(
                "GET",
                f"/api/v1/slo/{slo_id}/history",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "from_ts": from_ts,
                    "to_ts": to_ts,
                    "target": target,
                },
            )

            history = data.get("data", {})
            return {
                "success": True,
                "slo_id": slo_id,
                "overall": history.get("overall"),
                "thresholds": history.get("thresholds"),
                "series": history.get("series"),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
