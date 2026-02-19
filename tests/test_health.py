"""Tests for health check functionality."""
import pytest
import json
from unittest.mock import MagicMock, patch

from src.core.health import (
    ConfluenceHealthCheck,
    perform_health_check,
    get_health_status_dict,
    HealthCheckResult,
)
from src.core.confluence_mock import create_mock_confluence


@pytest.fixture
def mock_confluence():
    """Fixture providing a mock Confluence client."""
    return create_mock_confluence()


class TestConfluenceHealthCheck:
    """Tests for ConfluenceHealthCheck class."""
    
    def test_health_check_healthy(self, mock_confluence):
        """Test health check returns healthy when Confluence is reachable."""
        health_checker = ConfluenceHealthCheck(mock_confluence)
        result = health_checker.check_connectivity()
        
        assert result["status"] == "healthy"
        assert "response_time_ms" in result
    
    def test_health_check_unhealthy(self):
        """Test health check returns unhealthy when Confluence is unreachable."""
        # Create a mock that raises an exception for get_server_info
        broken_client = MagicMock()
        broken_client.get_server_info.side_effect = Exception("Connection refused")
        
        health_checker = ConfluenceHealthCheck(broken_client)
        result = health_checker.check_connectivity()
        
        assert result["status"] == "unhealthy"
        assert "Connection refused" in result["message"]
    
    def test_health_check_api_limits(self, mock_confluence):
        """Test API limits check returns unknown."""
        health_checker = ConfluenceHealthCheck(mock_confluence)
        result = health_checker.check_api_limits()
        
        assert result["status"] == "unknown"


class TestPerformHealthCheck:
    """Tests for perform_health_check function."""
    
    def test_perform_health_check_healthy(self, mock_confluence):
        """Test full health check returns healthy result."""
        result = perform_health_check(mock_confluence)
        
        assert isinstance(result, HealthCheckResult)
        assert result.status == "healthy"
        assert "confluence_connectivity" in result.checks
        assert "server" in result.checks
        assert "api_limits" in result.checks
    
    def test_perform_health_check_unhealthy(self):
        """Test full health check returns unhealthy when Confluence is down."""
        broken_client = MagicMock()
        broken_client.get_server_info.side_effect = Exception("Connection refused")
        
        result = perform_health_check(broken_client)
        
        assert result.status == "unhealthy"
        assert result.checks["confluence_connectivity"]["status"] == "unhealthy"


class TestGetHealthStatusDict:
    """Tests for get_health_status_dict function."""
    
    def test_returns_valid_json_dict(self, mock_confluence):
        """Test health status can be serialized to JSON."""
        result = get_health_status_dict(mock_confluence)
        
        # Should be serializable to JSON
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        assert "status" in parsed
        assert "timestamp" in parsed
        assert "duration_ms" in parsed
        assert "checks" in parsed
    
    def test_includes_all_checks(self, mock_confluence):
        """Test health status includes all required checks."""
        result = get_health_status_dict(mock_confluence)
        
        checks = result["checks"]
        assert "server" in checks
        assert "confluence_connectivity" in checks
        assert "api_limits" in checks


class TestHealthCheckIntegration:
    """Integration tests for health check with MCP tools."""
    
    def test_health_check_tool_exists(self):
        """Test that health check tool can be created."""
        from src.transports.stdio_mode import create_mcp_app
        
        mock = create_mock_confluence()
        app = create_mcp_app(confluence_client=mock, use_mock=True)
        
        # Verify app was created (tool registration is internal to FastMCP)
        assert app is not None
        assert app.name == "Confluence-MCP-Server"
    
    def test_health_check_returns_json(self, mock_confluence):
        """Test health check tool returns JSON string."""
        from src.transports.stdio_mode import get_health_status_dict
        
        result = get_health_status_dict(mock_confluence)
        
        # Should be valid JSON
        json_str = json.dumps(result, indent=2)
        parsed = json.loads(json_str)
        
        assert parsed["status"] == "healthy"
