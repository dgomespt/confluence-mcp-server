"""Confluence module for Confluence MCP Server.

This module provides integration with Confluence API, including:
- Core Confluence operations (search, get page content, list pages)
- MCP tool registration
- Client configuration

Key Components:
- operations: Core Confluence API operations
- mcp_integration: MCP app factory and tool registration
"""

from src.modules.confluence.operations import (
    search_confluence_impl,
    get_page_content_impl,
    list_pages_impl,
)
from src.modules.confluence.mcp_integration import create_mcp_app

__all__ = [
    "search_confluence_impl",
    "get_page_content_impl",
    "list_pages_impl",
    "create_mcp_app",
]
