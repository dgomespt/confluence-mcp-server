"""MCP integration for the Confluence module."""
from typing import Optional

from mcp.server.fastmcp import FastMCP

from src.core.config import Config, get_confluence_client
from src.core.confluence_mock import ConfluenceMock, create_mock_confluence
from src.core.error_handling import handle_api_errors, log_api_call
from src.core.health import get_health_status_dict
from src.modules.confluence.operations import (
    search_confluence_impl,
    get_page_content_impl,
    list_pages_impl,
)


def create_mcp_app(
    confluence_client=None,
    use_mock: bool = False,
    include_metrics: bool = False
) -> FastMCP:
    """Create and configure the FastMCP application for Confluence integration.
    
    Args:
        confluence_client: Optional Confluence client. If not provided and
                          use_mock is False, will try to create from config.
        use_mock: If True, use a mock Confluence client for testing.
        include_metrics: If True, include metrics collection for tool invocations.
    
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
        if include_metrics:
            from src.core.metrics import (
                record_tool_invocation,
                record_tool_duration,
                record_tool_error
            )
            import time
            start_time = time.time()
            try:
                result = search_confluence_impl(confluence, query, limit)
                record_tool_invocation("search_confluence", "success")
                return result
            except Exception as e:
                record_tool_invocation("search_confluence", "error")
                record_tool_error("search_confluence", type(e).__name__)
                raise
            finally:
                record_tool_duration("search_confluence", time.time() - start_time)
        else:
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
        if include_metrics:
            from src.core.metrics import (
                record_tool_invocation,
                record_tool_duration,
                record_tool_error
            )
            import time
            start_time = time.time()
            try:
                result = get_page_content_impl(confluence, page_id, convert_to_markdown)
                record_tool_invocation("get_page_content", "success")
                return result
            except Exception as e:
                record_tool_invocation("get_page_content", "error")
                record_tool_error("get_page_content", type(e).__name__)
                raise
            finally:
                record_tool_duration("get_page_content", time.time() - start_time)
        else:
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
        if include_metrics:
            from src.core.metrics import (
                record_tool_invocation,
                record_tool_duration,
                record_tool_error
            )
            import time
            start_time = time.time()
            try:
                result = list_pages_impl(confluence, space, limit)
                record_tool_invocation("list_pages", "success")
                return result
            except Exception as e:
                record_tool_invocation("list_pages", "error")
                record_tool_error("list_pages", type(e).__name__)
                raise
            finally:
                record_tool_duration("list_pages", time.time() - start_time)
        else:
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
        if include_metrics:
            from src.core.metrics import record_tool_invocation, record_tool_duration
            import time
            start_time = time.time()
            try:
                health_status = get_health_status_dict(confluence)
                record_tool_invocation("health_check", "success")
                return json.dumps(health_status, indent=2)
            finally:
                record_tool_duration("health_check", time.time() - start_time)
        else:
            health_status = get_health_status_dict(confluence)
            return json.dumps(health_status, indent=2)

    return mcp
