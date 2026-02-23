"""Tests for the Confluence module integration and metrics."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.modules.confluence import create_mcp_app
from src.core.confluence_mock import create_mock_confluence, ConfluenceMock


class TestConfluenceModule:
    """Tests for the Confluence module integration."""
    
    def test_create_app_with_metrics(self):
        """Test that create_mcp_app can be created with include_metrics=True."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
        assert hasattr(app, 'confluence')
    
    @patch('src.modules.confluence.mcp_integration.Config.from_env')
    @patch('src.modules.confluence.mcp_integration.get_confluence_client')
    def test_create_app_with_environment_config(self, mock_get_client, mock_from_env):
        """Test that create_mcp_app can create a real Confluence client from environment variables."""
        mock_config = MagicMock()
        mock_confluence = MagicMock()
        
        mock_from_env.return_value = mock_config
        mock_get_client.return_value = mock_confluence
        
        app = create_mcp_app(use_mock=False)
        
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
        assert hasattr(app, 'confluence')
        mock_from_env.assert_called_once()
        mock_get_client.assert_called_once_with(mock_config)
    
    @patch('src.modules.confluence.mcp_integration.Config.from_env')
    def test_create_app_with_env_error(self, mock_from_env):
        """Test that create_mcp_app falls back to mock when environment config fails."""
        mock_from_env.side_effect = ValueError("Missing required environment variable")
        
        app = create_mcp_app(use_mock=False)
        
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
        assert hasattr(app, 'confluence')
        assert isinstance(app.confluence, ConfluenceMock)
    
    def test_search_confluence_with_metrics(self):
        """Test search_confluence tool with metrics enabled."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        # Get list of tools
        tools = asyncio.run(app.list_tools())
        tool_names = [tool.name for tool in tools]
        assert 'search_confluence' in tool_names
    
    def test_get_page_content_with_metrics(self):
        """Test get_page_content tool with metrics enabled."""
        mock = create_mcp_app(use_mock=True, include_metrics=True).confluence
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        tools = asyncio.run(app.list_tools())
        tool_names = [tool.name for tool in tools]
        assert 'get_page_content' in tool_names
    
    def test_list_pages_with_metrics(self):
        """Test list_pages tool with metrics enabled."""
        mock = create_mcp_app(use_mock=True, include_metrics=True).confluence
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        tools = asyncio.run(app.list_tools())
        tool_names = [tool.name for tool in tools]
        assert 'list_pages' in tool_names
    
    def test_health_check_with_metrics(self):
        """Test health_check tool with metrics enabled."""
        mock = create_mcp_app(use_mock=True, include_metrics=True).confluence
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        tools = asyncio.run(app.list_tools())
        tool_names = [tool.name for tool in tools]
        assert 'health_check' in tool_names
    
    @patch('src.core.metrics.record_tool_invocation')
    @patch('src.core.metrics.record_tool_duration')
    def test_search_metrics_integration(self, mock_record_duration, mock_record_invocation):
        """Test that search_confluence tool records metrics when include_metrics=True."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        # Invoke tool directly
        asyncio.run(app.call_tool('search_confluence', {"query": "onboarding"}))
        
        # Verify metrics were recorded
        mock_record_invocation.assert_called_once_with('search_confluence', 'success')
        mock_record_duration.assert_called_once()
    
    @patch('src.core.metrics.record_tool_invocation')
    @patch('src.core.metrics.record_tool_duration')
    def test_get_page_metrics_integration(self, mock_record_duration, mock_record_invocation):
        """Test that get_page_content tool records metrics when include_metrics=True."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        asyncio.run(app.call_tool('get_page_content', {"page_id": "101"}))
        
        mock_record_invocation.assert_called_once_with('get_page_content', 'success')
        mock_record_duration.assert_called_once()
    
    @patch('src.core.metrics.record_tool_invocation')
    @patch('src.core.metrics.record_tool_duration')
    def test_list_pages_metrics_integration(self, mock_record_duration, mock_record_invocation):
        """Test that list_pages tool records metrics when include_metrics=True."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        asyncio.run(app.call_tool('list_pages', {"space": "ENG"}))
        
        mock_record_invocation.assert_called_once_with('list_pages', 'success')
        mock_record_duration.assert_called_once()
    
    @patch('src.core.metrics.record_tool_invocation')
    @patch('src.core.metrics.record_tool_duration')
    def test_health_check_metrics_integration(self, mock_record_duration, mock_record_invocation):
        """Test that health_check tool records metrics when include_metrics=True."""
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True, include_metrics=True)
        
        asyncio.run(app.call_tool('health_check', {}))
        
        mock_record_invocation.assert_called_once_with('health_check', 'success')
        mock_record_duration.assert_called_once()
