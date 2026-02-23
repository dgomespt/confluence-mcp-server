"""Core Confluence operations for the MCP server."""
import os
from typing import Any, Dict, List, Optional

from src.core.html_utils import html_to_markdown
from src.core.logging_config import get_logger
from src.core.validators import (
    validate_limit,
    validate_page_id,
    validate_query,
    validate_space_key,
)
from src.core.exceptions import ConfluenceNotFoundError

# Initialize logger
logger = get_logger("confluence.operations")


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
