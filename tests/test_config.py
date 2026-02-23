"""Tests for the configuration module."""
import os
import pytest
from unittest.mock import patch

from src.core.config import Config, get_confluence_client


class TestConfig:
    """Tests for the Config class."""
    
    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USERNAME': 'test@example.com',
        'CONFLUENCE_API_TOKEN': 'test-token',
        'MCP_TRANSPORT': 'sse',
        'MCP_HOST': '0.0.0.0',
        'MCP_PORT': '9090'
    })
    def test_from_env_with_all_variables(self):
        """Test creating Config from all environment variables."""
        config = Config.from_env()
        
        assert config.confluence_url == 'https://test.atlassian.net'
        assert config.confluence_username == 'test@example.com'
        assert config.confluence_api_token == 'test-token'
        assert config.transport == 'sse'
        assert config.host == '0.0.0.0'
        assert config.port == 9090
    
    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USERNAME': 'test@example.com',
        'CONFLUENCE_API_TOKEN': 'test-token'
    })
    def test_from_env_with_defaults(self):
        """Test creating Config with only required variables and defaults."""
        config = Config.from_env()
        
        assert config.transport == 'stdio'
        assert config.host == '127.0.0.1'
        assert config.port == 8080
    
    @patch.dict(os.environ, {})
    def test_from_env_missing_required_variables(self):
        """Test that from_env raises ValueError when required variables are missing."""
        with pytest.raises(ValueError):
            Config.from_env()
    
    @patch.dict(os.environ, {})
    def test_from_env_optional_returns_none(self):
        """Test that from_env_optional returns None when variables are missing."""
        config = Config.from_env_optional()
        assert config is None
    
    @patch.dict(os.environ, {
        'CONFLUENCE_URL': 'https://test.atlassian.net',
        'CONFLUENCE_USERNAME': 'test@example.com',
        'CONFLUENCE_API_TOKEN': 'test-token'
    })
    def test_from_env_optional_returns_config(self):
        """Test that from_env_optional returns a config when variables are present."""
        config = Config.from_env_optional()
        assert isinstance(config, Config)
        assert config.confluence_url == 'https://test.atlassian.net'
    
    @patch('atlassian.Confluence')
    def test_get_confluence_client(self, mock_confluence_class):
        """Test that get_confluence_client creates a Confluence client from config."""
        mock_confluence_instance = mock_confluence_class.return_value
        
        config = Config(
            confluence_url='https://test.atlassian.net',
            confluence_username='test@example.com',
            confluence_api_token='test-token'
        )
        
        client = get_confluence_client(config)
        
        mock_confluence_class.assert_called_once_with(
            url=config.confluence_url,
            username=config.confluence_username,
            password=config.confluence_api_token,
            cloud=True
        )
        assert client == mock_confluence_instance
