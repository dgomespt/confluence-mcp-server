# Development

## Running Tests

```bash
pytest tests/
```

## Testing with MCP Inspector

MCP Inspector is a local web-based tool that lets you test your MCP server without requiring Claude Desktop or any external AI service. It's perfect for debugging and manual testing.

### Installation

MCP Inspector requires Node.js. If you don't have it installed, download from [nodejs.org](https://nodejs.org/).

You also need the MCP Python package:

```bash
pip install mcp
```

### Running MCP Inspector

#### Option 1: Using the Built-in Mock (No Credentials Needed)

Your server includes a mock Confluence client with pre-populated test data. This is the fastest way to get started:

```bash
npx @modelcontextprotocol/inspector python -m src.main
```

#### Option 2: With Real Confluence Credentials

If you want to test against a real Confluence instance:

```bash
npx @modelcontextprotocol/inspector python -m src.main \
  --env CONFLUENCE_URL=https://your-domain.atlassian.net \
  --env CONFLUENCE_USERNAME=your-email@example.com \
  --env CONFLUENCE_API_TOKEN=your-api-token
```

#### Option 3: For SSE Transport

```bash
npx @modelcontextprotocol/inspector python -m src.main --transport sse
```

### Using the Inspector UI

Once MCP Inspector starts, it will open a web interface where you can:

1. **View Tools** - See all available MCP tools (search_confluence, get_page_content, list_pages)
2. **Invoke Tools** - Select any tool, fill in parameters, and execute
3. **View Responses** - See formatted JSON responses
4. **Debug** - View server logs and debugging information

#### Example Tests

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

## Project Structure

```
confluence-mcp-server-example/
├── .github/
│   └── workflows/
│       └── main.yml         # CI/CD pipeline with GitHub Actions
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
