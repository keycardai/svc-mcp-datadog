"""Metric Tools.

Tools for Datadog metrics: query_metrics, list_active_metrics.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_metric_tools(mcp: FastMCP) -> None:
    """Register metric tools with the MCP server."""

    @mcp.tool(
        name="query_metrics",
        description="Query timeseries metric data from Datadog. Returns data points for a metric query over a time range. Example query: 'avg:system.cpu.user{host:myhost}'.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def query_metrics(
        ctx: Context,
        query: str,
        from_ts: int,
        to_ts: int,
    ) -> dict:
        """Query timeseries metric data.

        Args:
            query: Datadog metric query string (e.g., "avg:system.cpu.user{host:myhost}").
            from_ts: Start of the query time range (Unix epoch seconds).
            to_ts: End of the query time range (Unix epoch seconds).
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/query",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "query": query,
                    "from": from_ts,
                    "to": to_ts,
                },
            )

            series = [
                {
                    "metric": s.get("metric"),
                    "display_name": s.get("display_name"),
                    "scope": s.get("scope"),
                    "expression": s.get("expression"),
                    "unit": s.get("unit"),
                    "pointlist": s.get("pointlist"),
                    "length": s.get("length"),
                    "start": s.get("start"),
                    "end": s.get("end"),
                    "interval": s.get("interval"),
                    "tag_set": s.get("tag_set"),
                }
                for s in data.get("series", [])
            ]
            return {
                "success": True,
                "series": series,
                "count": len(series),
                "from_date": data.get("from_date"),
                "to_date": data.get("to_date"),
                "query": data.get("query"),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="list_active_metrics",
        description="List actively reporting metrics in Datadog from a given time. Optionally filter by host or tag.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def list_active_metrics(
        ctx: Context,
        from_ts: int,
        host: str | None = None,
        tag_filter: str | None = None,
    ) -> dict:
        """List active metrics.

        Args:
            from_ts: Seconds since Unix epoch; only return metrics reported since this time.
            host: Filter metrics by hostname.
            tag_filter: Filter metrics by tag (e.g., "env:prod").
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/metrics",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "from": from_ts,
                    "host": host,
                    "tag_filter": tag_filter,
                },
            )

            metrics = data.get("metrics", [])
            return {
                "success": True,
                "metrics": metrics,
                "count": len(metrics),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
