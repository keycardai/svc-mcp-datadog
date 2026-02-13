"""Event Tools.

Tools for Datadog events: list_events.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_event_tools(mcp: FastMCP) -> None:
    """Register event tools with the MCP server."""

    @mcp.tool(
        name="list_events",
        description="Search events from the Datadog event stream. Filter by query, time range, and pagination.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def list_events(
        ctx: Context,
        filter_query: str | None = None,
        filter_from: str | None = None,
        filter_to: str | None = None,
        sort: str = "-timestamp",
        page_limit: int = 10,
        page_cursor: str | None = None,
    ) -> dict:
        """List events from the event stream.

        Args:
            filter_query: Search query to filter events (e.g., "source:nginx priority:normal").
            filter_from: Start time (ISO 8601 or relative like "now-24h").
            filter_to: End time (ISO 8601 or relative like "now").
            sort: Sort order: "timestamp" (asc) or "-timestamp" (desc).
            page_limit: Number of events per page (max 1000).
            page_cursor: Pagination cursor from previous response.
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v2/events",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "filter[query]": filter_query,
                    "filter[from]": filter_from,
                    "filter[to]": filter_to,
                    "sort": sort,
                    "page[limit]": page_limit,
                    "page[cursor]": page_cursor,
                },
            )

            events = [
                {
                    "id": evt.get("id"),
                    "type": evt.get("type"),
                    "timestamp": evt.get("attributes", {}).get("timestamp"),
                    "title": evt.get("attributes", {}).get("evt", {}).get("name"),
                    "message": evt.get("attributes", {}).get("message"),
                    "tags": evt.get("attributes", {}).get("tags"),
                    "status": evt.get("attributes", {}).get("status"),
                }
                for evt in data.get("data", [])
            ]

            next_cursor = data.get("meta", {}).get("page", {}).get("after")
            return {
                "success": True,
                "events": events,
                "count": len(events),
                "next_cursor": next_cursor,
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
