# Usage

## STDIO Mode (Local Integration)

Run the server in STDIO mode for integration with Claude Code, Cursor, or other MCP-compatible tools:

```bash
python -m src.main
```

Or directly:
```bash
python -m src.transports.stdio_mode
```

## SSE Mode (Remote Server)

Run as a remote server that clients can connect to via HTTP:

```bash
export MCP_TRANSPORT=sse
python -m src.main
```

The server will start on `http://0.0.0.0:8080`.

## Using with Claude Code

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

## Using Docker

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

### Using with Claude Desktop (Docker)

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
