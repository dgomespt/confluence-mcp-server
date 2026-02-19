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
from src.core.logging_config import get_logger, setup_logging
from src.core.validators import (
    validate_limit,
    validate_page_id,
    validate_query,
    validate_space_key,
)
from src.core.error_handling import handle_api_errors, log_api_call
from src.core.exceptions import ConfluenceNotFoundError
from src.core.health import get_health_status_dict


# Initialize logger
logger = get_logger("sse_mode")


def search_confluence_impl(confluence, query: str, limit: int = 5) -> str:
    """Search for Confluence pages and blogs using a query string.
    
    Args:
        confluence: The Confluence client instance.
        query: The search query string.
        limit: Maximum number of results to return (default: 5).
    
    Returns:
        Formatted search results with titles, IDs, and links.
    """
    # Validate inputs
    query = validate_query(query)
    limit = validate_limit(limit)
    
    logger.info(f"Searching Confluence for: '{query}' (limit: {limit})")
    
    results = confluence.cql(f'text ~ "{query}"', limit=limit)
    
    output = []
    for item in results.get('results', []):
        title = item['content']['title']
        page_id = item['content']['id']
        # Get confluence URL from client or use environment
        base_url = getattr(confluence, 'url', None) or os.getenv('CONFLUENCE_URL', '')
        url = f"{base_url}/wiki{item['content']['_links']['webui']}"
        output.append(f"- {title} (ID: {page_id})\n  Link: {url}")
    
    result_str = "\n".join(output) if output else "No results found."
    logger.info(f"Search completed. Found {len(output)} results for query: '{query}'")
    
    return result_str


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
    # Validate inputs
    page_id = validate_page_id(page_id)
    
    logger.info(f"Getting page content for ID: {page_id}")
    
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage')
    except Exception as e:
        logger.warning(f"Page not found: {page_id}")
        raise ConfluenceNotFoundError("Page", page_id)
    
    title = page.get('title')
    html_body = page.get('body', {}).get('storage', {}).get('value', '')
    
    if convert_to_markdown:
        content = html_to_markdown(html_body)
    else:
        content = html_body
    
    result = f"Title: {title}\n\n{content}"
    logger.info(f"Retrieved content for page: {title} (ID: {page_id})")
    
    return result


def list_pages_impl(confluence, space: str = "ENG", limit: int = 10) -> str:
    """List all pages in a Confluence space.
    
    Args:
        confluence: The Confluence client instance.
        space: The Confluence space key (default: ENG).
        limit: Maximum number of results to return (default: 10).
    
    Returns:
        Formatted list of pages with titles, IDs, and links.
    """
    # Validate inputs
    space = validate_space_key(space)
    limit = validate_limit(limit)
    
    logger.info(f"Listing pages in space: {space} (limit: {limit})")
    
    results = confluence.cql(f"space={space} AND type=page", limit=limit)
    
    output = []
    for item in results.get('results', []):
        title = item['content']['title']
        page_id = item['content']['id']
        base_url = getattr(confluence, 'url', None) or os.getenv('CONFLUENCE_URL', '')
        url = f"{base_url}/wiki{item['content']['_links']['webui']}"
        output.append(f"- {title} (ID: {page_id})\n  Link: {url}")
    
    result_str = "\n".join(output) if output else f"No pages found in space {space}."
    logger.info(f"Listed {len(output)} pages in space: {space}")
    
    return result_str


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
    @handle_api_errors
    @log_api_call
    def search_confluence(query: str, limit: int = 5) -> str:
        """Search Confluence pages and blogs.
        
        Args:
            query: The search query string.
            limit: Maximum number of results (default: 5, max: 100).
        
        Returns:
            Formatted search results with titles, IDs, and links.
        """
        return search_confluence_impl(confluence, query, limit)

    @mcp.tool()
    @handle_api_errors
    @log_api_call
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
    @handle_api_errors
    @log_api_call
    def list_pages(space: str = "ENG", limit: int = 10) -> str:
        """List all pages in a Confluence space.
        
        Args:
            space: The Confluence space key (default: ENG).
            limit: Maximum number of results (default: 10, max: 100).
        
        Returns:
            Formatted list of pages with titles, IDs, and links.
        """
        return list_pages_impl(confluence, space, limit)

    @mcp.tool()
    @handle_api_errors
    @log_api_call
    def health_check() -> str:
        """Check the health status of the MCP server and Confluence connection.
        
        Returns:
            JSON string with health status information.
        """
        import json
        health_status = get_health_status_dict(confluence)
        return json.dumps(health_status, indent=2)

    return mcp


def run_sse(host: str = "0.0.0.0", port: int = 8080):
    """Run the MCP server in SSE mode.
    
    Args:
        host: Host to bind to (default: 0.0.0.0).
        port: Port to bind to (default: 8080).
    """
    # Setup logging
    structured = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
    setup_logging(structured=structured)
    
    logger.info(f"Starting Confluence MCP Server in SSE mode on {host}:{port}")
    
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
