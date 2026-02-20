# Observability

The server includes comprehensive observability features for production monitoring.

## Prometheus Metrics

When running in SSE mode, a `/metrics` endpoint is available for Prometheus to scrape:

```bash
# Start SSE server with metrics
export MCP_TRANSPORT=sse
python -m src.main

# Scrape metrics
curl http://localhost:8080/metrics
```

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `confluence_mcp_tool_invocations_total` | Counter | Total tool invocations by name + status |
| `confluence_mcp_tool_duration_seconds` | Histogram | Tool execution time |
| `confluence_mcp_tool_errors_total` | Counter | Errors by tool + error type |
| `confluence_mcp_http_requests_total` | Counter | HTTP requests by method/endpoint/status |
| `confluence_mcp_http_request_duration_seconds` | Histogram | HTTP request duration |
| `confluence_mcp_server_start_time_seconds` | Gauge | Server start timestamp |
| `confluence_mcp_server_uptime_seconds` | Gauge | Server uptime in seconds |
| `confluence_mcp_active_connections` | Gauge | Active connections |

## Health Check

A `/health` endpoint is also available:

```bash
curl http://localhost:8080/health
```

## Structured Logging

Configure logging with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO |
| `LOG_STRUCTURED` | Set to "true" for JSON output | false |
| `LOG_FILE` | Optional file path for log output | stdout |
