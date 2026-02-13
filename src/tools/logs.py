"""Log Tools.

Tools for Datadog logs: search_logs.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_log_tools(mcp: FastMCP) -> None:
    """Register log tools with the MCP server."""

    @mcp.tool(
        name="search_logs",
        description="Search and filter log events in Datadog. Supports Datadog log search query syntax (e.g., 'service:web status:error').",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def search_logs(
        ctx: Context,
        query: str = "*",
        from_ts: str | None = None,
        to_ts: str | None = None,
        limit: int = 25,
        sort: str = "-timestamp",
        cursor: str | None = None,
    ) -> dict:
        """Search log events.

        Args:
            query: Log search query using Datadog syntax (e.g., "service:web status:error").
            from_ts: Start time (ISO 8601 string or relative like "now-1h").
            to_ts: End time (ISO 8601 string or relative like "now").
            limit: Maximum number of logs to return (max 1000).
            sort: Sort order: "timestamp" (asc) or "-timestamp" (desc).
            cursor: Pagination cursor from previous response.
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            body = {
                "filter": {
                    "query": query,
                    "from": from_ts,
                    "to": to_ts,
                },
                "page": {
                    "limit": limit,
                    "cursor": cursor,
                },
                "sort": sort,
            }

            data = await request(
                "POST",
                "/api/v2/logs/events/search",
                api_key=creds.api_key,
                application_key=creds.application_key,
                json=body,
            )

            logs = [
                {
                    "id": log.get("id"),
                    "timestamp": log.get("attributes", {}).get("timestamp"),
                    "status": log.get("attributes", {}).get("status"),
                    "service": log.get("attributes", {}).get("service"),
                    "message": log.get("attributes", {}).get("message"),
                    "host": log.get("attributes", {}).get("host"),
                    "tags": log.get("attributes", {}).get("tags"),
                }
                for log in data.get("data", [])
            ]

            next_cursor = data.get("meta", {}).get("page", {}).get("after")
            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "next_cursor": next_cursor,
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
