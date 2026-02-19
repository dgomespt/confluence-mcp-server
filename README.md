# Confluence MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Confluence. This server can run in either STDIO mode (for local integration with Claude Code, Cursor, etc.) or SSE mode (for remote server deployment).

## Features

- **Search Confluence**: Search pages and blogs using CQL (Confluence Query Language)
- **Get Page Content**: Retrieve full content of any Confluence page by ID
- **List Pages**: List all pages in a specific Confluence space

## Requirements

- Python 3.11+
- Confluence Cloud or Data Center instance

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd confluence-mcp-server-example
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure your credentials:
```bash
cp .env.example .env
# Edit .env with your Confluence credentials
```

## Configuration

Set the following environment variables:

| Variable | Description |
|----------|-------------|
| `CONFLUENCE_URL` | Your Confluence instance URL (e.g., `https://your-domain.atlassian.net`) |
| `CONFLUENCE_USERNAME` | Your Confluence username (usually email) |
| `CONFLUENCE_API_TOKEN` | Your Atlassian API token |
| `MCP_TRANSPORT` | Transport mode: `stdio` (default) or `sse` |
| `MCP_HOST` | Host for SSE mode (default: `0.0.0.0`) |
| `MCP_PORT` | Port for SSE mode (default: `8080`) |

To generate an API token:
1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create a new API token
3. Use the token in your `.env` file

## Usage

### STDIO Mode (Local Integration)

Run the server in STDIO mode for integration with Claude Code, Cursor, or other MCP-compatible tools:

```bash
python -m src.main
```

Or directly:
```bash
python -m src.transports.stdio_mode
```

### SSE Mode (Remote Server)

Run as a remote server that clients can connect to via HTTP:

```bash
export MCP_TRANSPORT=sse
python -m src.main
```

The server will start on `http://0.0.0.0:8080`.

### Using with Claude Code

1. Configure your MCP settings to point to this server:

```json
{
  "mcpServers": {
    "confluence": {
      "command": "python",
      "args": ["-m", "src.main"],
      "env": {
        "CONFLUENCE_URL": "https://your-domain.atlassian.net",
        "CONFLUENCE_USERNAME": "your-email@example.com",
        "CONFLUENCE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Using Docker

Build and run with Docker Compose using profiles:

```bash
# Edit .env with your credentials

# STDIO mode (for Claude Desktop - interactive):
docker compose --profile stdio run confluence-mcp

# SSE mode (for network clients - runs in background):
docker compose --profile sse up -d
```

**Services:**
- `confluence-mcp` (stdio profile): STDIO transport, no port exposed, interactive TTY
- `confluence-mcp-sse` (sse profile): SSE transport, exposes port 8080, runs as daemon

#### Using with Claude Desktop (Docker)

To use Docker with Claude Desktop, configure your MCP settings:

**Windows (Docker Desktop):**

```json
{
  "mcpServers": {
    "confluence": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network=host",
        "-e",
        "CONFLUENCE_URL=${CONFLUENCE_URL}",
        "-e",
        "CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME}",
        "-e",
        "CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN}",
        "confluence-mcp-server-example-confluence-mcp"
      ]
    }
  }
}
```

> **Note:** For Windows, you may need to adjust `--network=host` based on your Docker Desktop networking setup. If not using host networking, ensure the container can reach your Confluence instance.

**Alternative: Using Docker Compose with Claude Desktop**

If you prefer using docker-compose directly:

1. Add a `claude` service to your `docker-compose.yml` or use the existing stdio service
2. Configure Claude Desktop to run the docker-compose command:

```json
{
  "mcpServers": {
    "confluence": {
      "command": "docker-compose",
      "args": ["run", "--rm", "confluence-mcp"]
    }
  }
}
```

Make sure your `.env` file is configured with your Confluence credentials before starting.

## Available Tools

### search_confluence

Search for Confluence pages and blogs using a query string.

**Parameters:**
- `query` (string, required): The search query
- `limit` (integer, optional): Maximum results to return (default: 5)

### get_page_content

Retrieve the full content of a specific page by its ID.

**Parameters:**
- `page_id` (string, required): The Confluence page ID

### list_pages

List all pages in a Confluence space.

**Parameters:**
- `space` (string, optional): The space key (default: "ENG")
- `limit` (integer, optional): Maximum results to return (default: 10)

## Development

### Running Tests

```bash
pytest tests/
```

### Testing with MCP Inspector

MCP Inspector is a local web-based tool that lets you test your MCP server without requiring Claude Desktop or any external AI service. It's perfect for debugging and manual testing.

#### Installation

MCP Inspector requires Node.js. If you don't have it installed, download from [nodejs.org](https://nodejs.org/).

You also need the MCP Python package:

```bash
pip install mcp
```

#### Running MCP Inspector

##### Option 1: Using the Built-in Mock (No Credentials Needed)

Your server includes a mock Confluence client with pre-populated test data. This is the fastest way to get started:

```bash
npx @modelcontextprotocol/inspector python -m src.main
```

##### Option 2: With Real Confluence Credentials

If you want to test against a real Confluence instance:

```bash
npx @modelcontextprotocol/inspector python -m src.main \
  --env CONFLUENCE_URL=https://your-domain.atlassian.net \
  --env CONFLUENCE_USERNAME=your-email@example.com \
  --env CONFLUENCE_API_TOKEN=your-api-token
```

##### Option 3: For SSE Transport

```bash
npx @modelcontextprotocol/inspector python -m src.main --transport sse
```

#### Using the Inspector UI

Once MCP Inspector starts, it will open a web interface where you can:

1. **View Tools** - See all available MCP tools (search_confluence, get_page_content, list_pages)
2. **Invoke Tools** - Select any tool, fill in parameters, and execute
3. **View Responses** - See formatted JSON responses
4. **Debug** - View server logs and debugging information

##### Example Tests

Try these in the inspector:

| Tool | Parameters | Expected Result |
|------|------------|-----------------|
| `search_confluence` | `{"query": "onboarding", "limit": 5}` | Returns "Onboarding Guide" |
| `get_page_content` | `{"page_id": "101"}` | Returns full page content |
| `list_pages` | `{"space": "ENG", "limit": 10}` | Lists ENG space pages |

The mock server comes pre-loaded with:
- Page ID `101`: "Onboarding Guide" (ENG space)
- Page ID `102`: "API Documentation" (DEV space)
- Page ID `103`: "Release Notes v1.0" (ENG space)

### Observability

The server includes comprehensive observability features for production monitoring.

#### Prometheus Metrics

When running in SSE mode, a `/metrics` endpoint is available for Prometheus to scrape:

```bash
# Start SSE server with metrics
export MCP_TRANSPORT=sse
python -m src.main

# Scrape metrics
curl http://localhost:8080/metrics
```

##### Available Metrics

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

#### Health Check

A `/health` endpoint is also available:

```bash
curl http://localhost:8080/health
```

#### Structured Logging

Configure logging with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO |
| `LOG_STRUCTURED` | Set to "true" for JSON output | false |
| `LOG_FILE` | Optional file path for log output | stdout |

### Project Structure

```
confluence-mcp-server-example/
├── src/
│   ├── main.py              # Main entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   └── confluence_mock.py  # Mock for testing
│   └── transports/
│       ├── stdio_mode.py    # STDIO transport
│       └── sse_mode.py      # SSE transport
├── tests/
│   └── test_stdio_mode.py  # Tests
├── docker/
│   └── Dockerfile           # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── .env.example            # Example environment variables
```

## Acknowledgments

This project was developed with assistance from:
- **Kilo Code** - AI coding assistant that helped implement production-ready features including error handling, retry logic, structured logging, input validation, and health checks
- **MiniMax M2.5** - AI model that powered the development process

## License

MIT
