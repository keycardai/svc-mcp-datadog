"""Trace/APM Tools.

Tools for Datadog APM: search_spans.
"""

from fastmcp import FastMCP, Context

from ..auth import get_datadog_credentials
from ..client import DatadogClientError, request


def register_trace_tools(mcp: FastMCP) -> None:
    """Register trace/APM tools with the MCP server."""

    @mcp.tool(
        name="search_spans",
        description="Search APM spans/traces in Datadog. Filter by service, operation, resource, and more using Datadog query syntax.",
    )
    async def search_spans(
        ctx: Context,
        query: str = "*",
        from_ts: str | None = None,
        to_ts: str | None = None,
        limit: int = 25,
        sort: str = "-timestamp",
        cursor: str | None = None,
    ) -> dict:
        """Search APM spans.

        Args:
            query: Span search query (e.g., "service:web-store operation_name:rails.request").
            from_ts: Start time (ISO 8601 or relative like "now-15m").
            to_ts: End time (ISO 8601 or relative like "now").
            limit: Maximum number of spans to return (max 1000).
            sort: Sort order: "timestamp" (asc) or "-timestamp" (desc).
            cursor: Pagination cursor from previous response.
        """
        try:
            creds = get_datadog_credentials()

            body = {
                "data": {
                    "type": "search_request",
                    "attributes": {
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
                    },
                }
            }

            data = await request(
                "POST",
                "/api/v2/spans/events/search",
                api_key=creds.api_key,
                application_key=creds.application_key,
                json=body,
            )

            spans = [
                {
                    "id": span.get("id"),
                    "type": span.get("type"),
                    "timestamp": span.get("attributes", {}).get("timestamp"),
                    "service": span.get("attributes", {}).get("service"),
                    "resource_name": span.get("attributes", {}).get("resource_name"),
                    "span_id": span.get("attributes", {}).get("span_id"),
                    "trace_id": span.get("attributes", {}).get("trace_id"),
                    "duration": span.get("attributes", {}).get("duration"),
                    "status": span.get("attributes", {}).get("status"),
                    "host": span.get("attributes", {}).get("host"),
                    "env": span.get("attributes", {}).get("env"),
                    "operation_name": span.get("attributes", {}).get("operation_name"),
                }
                for span in data.get("data", [])
            ]

            next_cursor = data.get("meta", {}).get("page", {}).get("after")
            return {
                "success": True,
                "spans": spans,
                "count": len(spans),
                "next_cursor": next_cursor,
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
