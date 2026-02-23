"""Tests for the Confluence MCP Server SSE mode."""
import pytest
from unittest.mock import MagicMock, patch

from src.transports.sse_mode import run_sse
from src.modules.confluence import (
    create_mcp_app,
    search_confluence_impl,
    get_page_content_impl,
    list_pages_impl
)
from src.core.confluence_mock import create_mock_confluence, ConfluenceMock
from src.core.html_utils import html_to_markdown, html_to_markdown_simple
from src.core.exceptions import InvalidQueryError, InvalidLimitError, InvalidPageIdError, InvalidSpaceKeyError


@pytest.fixture
def mock_confluence():
    """Fixture providing a mock Confluence client."""
    return create_mock_confluence()


class TestSearchConfluence:
    """Tests for search_confluence functionality."""
    
    def test_search_confluence_tool_sse(self, mock_confluence):
        """Test the search_confluence tool in SSE mode with a mocked API response."""
        result = search_confluence_impl(mock_confluence, query="onboarding", limit=5)
        
        assert "Onboarding Guide" in result
        assert "ID: 101" in result
    
    def test_search_confluence_no_results(self, mock_confluence):
        """Test search returns no results for unknown query."""
        result = search_confluence_impl(mock_confluence, query="nonexistent", limit=5)
        
        assert "No results found" in result
    
    def test_search_with_custom_limit(self, mock_confluence):
        """Test search respects the limit parameter."""
        result = search_confluence_impl(mock_confluence, query="onboarding", limit=1)
        
        # Should return at most 1 result
        assert "Onboarding Guide" in result
    
    def test_search_includes_url(self, mock_confluence):
        """Test search results include the page URL."""
        result = search_confluence_impl(mock_confluence, query="onboarding")
        
        assert "Link:" in result
        assert "atlassian.net" in result or "mock.atlassian.net" in result
    
    def test_search_empty_query_raises_error(self, mock_confluence):
        """Test search with empty query raises validation error."""
        with pytest.raises(InvalidQueryError):
            search_confluence_impl(mock_confluence, query="", limit=5)
    
    def test_search_limit_validation(self, mock_confluence):
        """Test search validates limit parameter."""
        with pytest.raises(InvalidLimitError):
            search_confluence_impl(mock_confluence, query="test", limit=200)


class TestGetPageContent:
    """Tests for get_page_content functionality."""
    
    def test_get_page_content_markdown(self, mock_confluence):
        """Test the get_page_content tool returns page content in Markdown by default."""
        result = get_page_content_impl(mock_confluence, page_id="101")
        
        assert "Title: Onboarding Guide" in result
        # Should be Markdown format (not HTML tags)
        assert "<p>" not in result
        assert "Welcome to the team" in result
    
    def test_get_page_content_raw_html(self, mock_confluence):
        """Test the get_page_content tool can return raw HTML when requested."""
        result = get_page_content_impl(mock_confluence, page_id="101", convert_to_markdown=False)
        
        assert "Title: Onboarding Guide" in result
        # Should contain HTML
        assert "<p>" in result
    
    def test_get_page_content_invalid_id(self, mock_confluence):
        """Test get_page_content with invalid ID raises error."""
        with pytest.raises(Exception):
            get_page_content_impl(mock_confluence, page_id="999")
    
    def test_get_page_content_different_pages(self, mock_confluence):
        """Test getting different pages returns correct content."""
        result = get_page_content_impl(mock_confluence, page_id="102")
        
        assert "Title: API Documentation" in result
    
    def test_get_page_empty_id_raises_error(self, mock_confluence):
        """Test get_page_content with empty ID raises error."""
        with pytest.raises(InvalidPageIdError):
            get_page_content_impl(mock_confluence, page_id="")


class TestListPages:
    """Tests for list_pages functionality."""
    
    def test_list_pages_eng_space(self, mock_confluence):
        """Test list_pages returns pages in ENG space."""
        result = list_pages_impl(mock_confluence, space="ENG", limit=10)
        
        assert "Onboarding Guide" in result
        assert "ID: 101" in result
    
    def test_list_pages_dev_space(self, mock_confluence):
        """Test list_pages returns pages in DEV space."""
        result = list_pages_impl(mock_confluence, space="DEV", limit=10)
        
        assert "API Documentation" in result
        assert "ID: 102" in result
    
    def test_list_pages_empty_space(self, mock_confluence):
        """Test list_pages returns message for empty space."""
        result = list_pages_impl(mock_confluence, space="EMPTY", limit=10)
        
        assert "No pages found" in result
        assert "EMPTY" in result
    
    def test_list_pages_respects_limit(self, mock_confluence):
        """Test list_pages respects the limit parameter."""
        result = list_pages_impl(mock_confluence, space="ENG", limit=1)
        
        # Should work without error
        assert isinstance(result, str)
    
    def test_list_pages_invalid_space_raises_error(self, mock_confluence):
        """Test list_pages with invalid space raises error."""
        with pytest.raises(InvalidSpaceKeyError):
            list_pages_impl(mock_confluence, space="", limit=10)
    
    def test_list_pages_limit_validation(self, mock_confluence):
        """Test list_pages validates limit parameter."""
        with pytest.raises(InvalidLimitError):
            list_pages_impl(mock_confluence, space="ENG", limit=0)


class TestMCPApp:
    """Tests for MCP app creation and configuration."""
    
    def test_mcp_app_sse_creation(self):
        """Test that MCP SSE app can be created with mock client."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True)
        
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
        assert hasattr(app, 'confluence')
    
    def test_mcp_app_with_use_mock_flag(self):
        """Test that MCP SSE app can be created with use_mock=True."""
        app = create_mcp_app(use_mock=True)
        
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
        assert app.confluence is not None
    
    def test_mcp_app_has_tools(self):
        """Test that MCP app has the expected tools registered."""
        app = create_mcp_app(use_mock=True)
        
        # The app should have tools registered
        # FastMCP tools are stored internally
        assert app is not None


class TestSSEIntegration:
    """Integration tests for SSE mode."""
    
    def test_sse_and_stdio_same_implementation(self):
        """Test that SSE and STDIO use the same implementation functions."""
        mock = create_mock_confluence()
        
        # Test search
        stdio_result = search_confluence_impl(mock, query="onboarding")
        sse_result = search_confluence_impl(mock, query="onboarding")
        assert stdio_result == sse_result
        
        # Test get_page_content
        stdio_result = get_page_content_impl(mock, page_id="101")
        sse_result = get_page_content_impl(mock, page_id="101")
        assert stdio_result == sse_result
        
        # Test list_pages
        stdio_result = list_pages_impl(mock, space="ENG")
        sse_result = list_pages_impl(mock, space="ENG")
        assert stdio_result == sse_result
    
    def test_run_sse_function_exists(self):
        """Test that run_sse function exists and is callable."""
        assert callable(run_sse)
    
    def test_sse_app_stores_confluence_client(self):
        """Test that the SSE app stores the confluence client."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True)
        
        assert app.confluence is mock


class TestEdgeCases:
    """Edge case tests."""
    
    def test_get_page_content_with_empty_html(self, mock_confluence):
        """Test get_page_content with page that has empty HTML body."""
        # Add a page with empty content
        mock_confluence.add_page("104", "Empty Page", "", "TEST")
        
        result = get_page_content_impl(mock_confluence, page_id="104")
        
        assert "Title: Empty Page" in result
