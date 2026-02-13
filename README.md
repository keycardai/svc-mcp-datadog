# Datadog MCP Server

MCP server for Datadog operations with Keycard authentication.

## Features

- List and inspect monitors and their alert status
- Search and list hosts in your infrastructure
- Query timeseries metrics and list active metrics
- Search logs with filtering and time ranges
- Browse events from your Datadog event stream
- List and inspect dashboards
- View incidents and their details
- Check SLO status and history
- Search APM traces and spans

## Setup

1. Copy `.env.example` to `.env` and fill in your Keycard credentials
2. Run `uv sync` to install dependencies
3. Run `uv run python -m src.server` to start the server

## Tools

### Monitor Tools
- `list_monitors` - List monitors, filter by name/tags/status
- `get_monitor` - Get monitor details, thresholds, and status

### Host Tools
- `list_hosts` - Search and list hosts in your infrastructure
- `get_host_totals` - Get active and up host counts

### Metric Tools
- `query_metrics` - Query timeseries metric data
- `list_active_metrics` - List actively reporting metrics

### Log Tools
- `search_logs` - Search logs with Datadog query syntax

### Event Tools
- `list_events` - Search events from the event stream

### Dashboard Tools
- `list_dashboards` - List all dashboards
- `get_dashboard` - Get dashboard details and widgets

### Incident Tools
- `list_incidents` - List incidents with status and severity
- `get_incident` - Get incident details and timeline

### SLO Tools
- `list_slos` - List Service Level Objectives
- `get_slo` - Get SLO config and targets
- `get_slo_history` - Get SLO performance over time

### Trace Tools
- `search_spans` - Search APM spans by service/operation

## Deployment

Deploy to Render using `render.yaml`.
