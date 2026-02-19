"""Tests for the Confluence MCP Server stdio mode."""
import pytest
from unittest.mock import MagicMock, patch

from src.transports.stdio_mode import (
    create_mcp_app,
    search_confluence_impl,
    get_page_content_impl,
    list_pages_impl
)
from src.core.confluence_mock import create_mock_confluence, ConfluenceMock


@pytest.fixture
def mock_confluence():
    """Fixture providing a mock Confluence client."""
    return create_mock_confluence()


def test_search_confluence_tool(mock_confluence):
    """Test the search_confluence tool with a mocked API response."""
    result = search_confluence_impl(mock_confluence, query="onboarding", limit=5)
    
    # Assertions
    assert "Onboarding Guide" in result
    assert "ID: 101" in result


def test_search_confluence_no_results(mock_confluence):
    """Test search returns no results for unknown query."""
    result = search_confluence_impl(mock_confluence, query="nonexistent", limit=5)
    
    assert "No results found" in result


def test_get_page_content_tool(mock_confluence):
    """Test the get_page_content tool returns page content in Markdown by default."""
    result = get_page_content_impl(mock_confluence, page_id="101")
    
    assert "Title: Onboarding Guide" in result
    # Should be Markdown format (not HTML tags)
    assert "<p>" not in result
    assert "Welcome to the team" in result


def test_get_page_content_raw_html(mock_confluence):
    """Test the get_page_content tool can return raw HTML when requested."""
    result = get_page_content_impl(mock_confluence, page_id="101", convert_to_markdown=False)
    
    assert "Title: Onboarding Guide" in result
    # Should contain HTML
    assert "<p>" in result


def test_get_page_content_invalid_id(mock_confluence):
    """Test get_page_content with invalid ID raises error."""
    with pytest.raises(Exception) as exc_info:
        get_page_content_impl(mock_confluence, page_id="999")
    
    assert "not found" in str(exc_info.value).lower()


def test_list_pages(mock_confluence):
    """Test list_pages returns pages in a space."""
    result = list_pages_impl(mock_confluence, space="ENG", limit=10)
    
    assert "Onboarding Guide" in result
    assert "ID: 101" in result


def test_mcp_app_creation():
    """Test that MCP app can be created with mock client."""
    mock = create_mock_confluence()
    app = create_mcp_app(confluence_client=mock, use_mock=True)
    
    assert app is not None
    assert app.name == "Confluence-MCP-Server"
    # Verify confluence is stored on the app
    assert hasattr(app, 'confluence')


def test_mcp_app_with_use_mock_flag():
    """Test that MCP app can be created with use_mock=True."""
    app = create_mcp_app(use_mock=True)
    
    assert app is not None
    assert app.name == "Confluence-MCP-Server"
    assert app.confluence is not None
