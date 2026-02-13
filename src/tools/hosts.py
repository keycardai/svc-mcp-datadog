"""Host Tools.

Tools for Datadog hosts: list_hosts, get_host_totals.
"""

from fastmcp import FastMCP, Context

from ..auth import auth_provider, get_datadog_credentials, DATADOG_API_URL
from ..client import DatadogClientError, request


def register_host_tools(mcp: FastMCP) -> None:
    """Register host tools with the MCP server."""

    @mcp.tool(
        name="list_hosts",
        description="Search and list hosts in your Datadog infrastructure. Filter by name, sort by CPU, load, or other metrics.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def list_hosts(
        ctx: Context,
        filter: str | None = None,
        sort_field: str | None = None,
        sort_dir: str | None = None,
        start: int = 0,
        count: int = 100,
        include_muted_hosts_data: bool = False,
    ) -> dict:
        """List hosts in the infrastructure.

        Args:
            filter: Search query string to filter hosts by name.
            sort_field: Field to sort by (e.g., "apps", "cpu", "iowait", "load").
            sort_dir: Sort direction: "asc" or "desc".
            start: Starting offset for pagination.
            count: Number of hosts to return (max 1000).
            include_muted_hosts_data: Include muted host information.
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/hosts",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "filter": filter,
                    "sort_field": sort_field,
                    "sort_dir": sort_dir,
                    "start": start,
                    "count": count,
                    "include_muted_hosts_data": str(include_muted_hosts_data).lower(),
                },
            )

            hosts = [
                {
                    "name": h.get("name"),
                    "id": h.get("id"),
                    "aliases": h.get("aliases"),
                    "apps": h.get("apps"),
                    "sources": h.get("sources"),
                    "up": h.get("up"),
                    "is_muted": h.get("is_muted"),
                    "last_reported_time": h.get("last_reported_time"),
                    "meta": h.get("meta"),
                }
                for h in data.get("host_list", [])
            ]
            return {
                "success": True,
                "hosts": hosts,
                "count": len(hosts),
                "total_matching": data.get("total_matching"),
                "total_returned": data.get("total_returned"),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}

    @mcp.tool(
        name="get_host_totals",
        description="Get total number of active and up hosts in your Datadog infrastructure.",
    )
    @auth_provider.grant(DATADOG_API_URL)
    async def get_host_totals(
        ctx: Context,
        from_ts: int | None = None,
    ) -> dict:
        """Get host count totals.

        Args:
            from_ts: Only count hosts that have reported since this Unix timestamp (seconds).
        """
        try:
            access_ctx = ctx.get_state("keycardai")
            creds = get_datadog_credentials(access_ctx)

            data = await request(
                "GET",
                "/api/v1/hosts/totals",
                api_key=creds.api_key,
                application_key=creds.application_key,
                params={
                    "from": from_ts,
                },
            )

            return {
                "success": True,
                "total_active": data.get("total_active"),
                "total_up": data.get("total_up"),
            }
        except DatadogClientError as e:
            return {"success": False, "error": e.message, "isError": True}
        except ValueError as e:
            return {"success": False, "error": str(e), "isError": True}
