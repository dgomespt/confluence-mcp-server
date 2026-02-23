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

## Quick Start

### Basic Usage

```bash
# Run in STDIO mode (default)
python -m src.main

# Run in SSE mode
export MCP_TRANSPORT=sse
python -m src.main
```

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

## Documentation

For more detailed information, see the documentation files in the `docs/` directory:

- [Usage Guide](docs/usage.md) - Detailed usage instructions for STDIO and SSE modes, Docker, and Claude Code integration
- [Development](docs/development.md) - Testing with MCP Inspector, running tests, and project structure
- [Observability](docs/observability.md) - Metrics, health checks, and logging configuration
- [CI/CD Pipeline](docs/cicd.md) - GitHub Actions workflow, testing, and deployment
- [Production Readiness](docs/production.md) - Security measures, performance optimization, and deployment guidelines

## Architecture

The server follows a modular architecture with clear separation of concerns:

- **Core Layer**: Contains shared functionality like error handling, logging, validation, and retry logic
- **Modules Layer**: Encapsulates specific functionality (Confluence integration) with operations and MCP integration
- **Transports Layer**: Handles communication between the server and clients using STDIO or SSE

## Project Structure

The main codebase is organized as:
- `src/modules/confluence/`: Confluence integration module
  - `operations.py`: Core API operations (search, get page content, list pages)
  - `mcp_integration.py`: MCP tool registration and app factory
- `src/core/`: Shared functionality
- `src/transports/`: STDIO and SSE communication modes

## Acknowledgments

This project was developed with assistance from:
- **Kilo Code** - AI coding assistant that helped implement production-ready features including error handling, retry logic, structured logging, input validation, and health checks
- **MiniMax M2.5** - AI model that powered the development process

## License

MIT
