"""SSE (Server-Sent Events) transport mode for Confluence MCP Server.

This transport mode allows the MCP server to run as a remote server
that clients can connect to via HTTP SSE.
"""
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP

from src.core.config import Config, get_confluence_client
from src.core.confluence_mock import ConfluenceMock, create_mock_confluence
from src.core.html_utils import html_to_markdown


def search_confluence_impl(confluence, query: str, limit: int = 5) -> str:
    """Search for Confluence pages and blogs using a query string.
    
    Args:
        confluence: The Confluence client instance.
        query: The search query string.
        limit: Maximum number of results to return (default: 5).
    
    Returns:
        Formatted search results with titles, IDs, and links.
    """
    results = confluence.cql(f'text ~ "{query}"', limit=limit)
    
    output = []
    for item in results.get('results', []):
        title = item['content']['title']
        page_id = item['content']['id']
        base_url = getattr(confluence, 'url', None) or os.getenv('CONFLUENCE_URL', '')
        url = f"{base_url}/wiki{item['content']['_links']['webui']}"
        output.append(f"- {title} (ID: {page_id})\n  Link: {url}")
        
    return "\n".join(output) if output else "No results found."


def get_page_content_impl(confluence, page_id: str, convert_to_markdown: bool = True) -> str:
    """Retrieve the full text content of a specific page by its ID.
    
    Args:
        confluence: The Confluence client instance.
        page_id: The Confluence page ID.
        convert_to_markdown: If True (default), convert HTML to Markdown for
                             better RAG/agent consumption. If False, return raw HTML.
    
    Returns:
        Page title and content in Markdown or HTML format.
    """
    page = confluence.get_page_by_id(page_id, expand='body.storage')
    title = page.get('title')
    html_body = page.get('body', {}).get('storage', {}).get('value', '')
    
    if convert_to_markdown:
        content = html_to_markdown(html_body)
    else:
        content = html_body
    
    return f"Title: {title}\n\n{content}"


def list_pages_impl(confluence, space: str = "ENG", limit: int = 10) -> str:
    """List all pages in a Confluence space.
    
    Args:
        confluence: The Confluence client instance.
        space: The Confluence space key (default: ENG).
        limit: Maximum number of results to return (default: 10).
    
    Returns:
        Formatted list of pages with titles, IDs, and links.
    """
    results = confluence.cql(f"space={space} AND type=page", limit=limit)
    
    output = []
    for item in results.get('results', []):
        title = item['content']['title']
        page_id = item['content']['id']
        base_url = getattr(confluence, 'url', None) or os.getenv('CONFLUENCE_URL', '')
        url = f"{base_url}/wiki{item['content']['_links']['webui']}"
        output.append(f"- {title} (ID: {page_id})\n  Link: {url}")
        
    return "\n".join(output) if output else f"No pages found in space {space}."


def create_mcp_app_sse(
    confluence_client=None,
    use_mock: bool = False
) -> FastMCP:
    """Create and configure the FastMCP application for SSE mode.
    
    Args:
        confluence_client: Optional Confluence client. If not provided and
                          use_mock is False, will try to create from config.
        use_mock: If True, use a mock Confluence client for testing.
    
    Returns:
        Configured FastMCP application.
    """
    mcp = FastMCP("Confluence-MCP-Server")
    
    # Get or create the Confluence client
    if use_mock:
        confluence = confluence_client or create_mock_confluence()
    elif confluence_client is not None:
        confluence = confluence_client
    else:
        # Try to get from environment
        try:
            config = Config.from_env()
            confluence = get_confluence_client(config)
        except ValueError:
            # If no env vars, use mock for testing
            confluence = create_mock_confluence()
    
    # Store confluence on app for testing access
    mcp.confluence = confluence
    
    @mcp.tool()
    def search_confluence(query: str, limit: int = 5) -> str:
        return search_confluence_impl(confluence, query, limit)

    @mcp.tool()
    def get_page_content(page_id: str, convert_to_markdown: bool = True) -> str:
        """Retrieve the content of a Confluence page.
        
        Args:
            page_id: The Confluence page ID.
            convert_to_markdown: Convert HTML to Markdown for better RAG/agent 
                                 consumption (default: True).
        
        Returns:
            Page content in Markdown (default) or HTML format.
        """
        return get_page_content_impl(confluence, page_id, convert_to_markdown)
    
    @mcp.tool()
    def list_pages(space: str = "ENG", limit: int = 10) -> str:
        return list_pages_impl(confluence, space, limit)

    return mcp


def run_sse(host: str = "0.0.0.0", port: int = 8080):
    """Run the MCP server in SSE mode.
    
    Args:
        host: Host to bind to (default: 0.0.0.0).
        port: Port to bind to (default: 8080).
    """
    mcp = create_mcp_app_sse()
    # FastMCP's run method with transport='sse' starts an SSE server
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Confluence MCP Server - SSE Mode")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    run_sse(host=args.host, port=args.port)
