"""Tests for Prometheus metrics in Confluence MCP Server."""
import time
import pytest
from unittest.mock import MagicMock, patch

from prometheus_client import REGISTRY


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset Prometheus metrics between tests to avoid state leakage."""
    # We can't easily reset prometheus_client counters, but we can
    # test relative changes by capturing values before and after
    yield


class TestMetricsModule:
    """Tests for the metrics module."""
    
    def test_metrics_module_imports(self):
        """Test that the metrics module can be imported."""
        from src.core.metrics import (
            TOOL_INVOCATIONS,
            TOOL_DURATION,
            TOOL_ERRORS,
            HTTP_REQUESTS,
            HTTP_DURATION,
            SERVER_START_TIME,
            SERVER_UPTIME,
            ACTIVE_CONNECTIONS,
        )
        assert TOOL_INVOCATIONS is not None
        assert TOOL_DURATION is not None
        assert TOOL_ERRORS is not None
        assert HTTP_REQUESTS is not None
        assert HTTP_DURATION is not None
        assert SERVER_START_TIME is not None
        assert SERVER_UPTIME is not None
        assert ACTIVE_CONNECTIONS is not None
    
    def test_get_metrics_returns_bytes(self):
        """Test that get_metrics returns bytes."""
        from src.core.metrics import get_metrics
        result = get_metrics()
        assert isinstance(result, bytes)
    
    def test_get_metrics_content_type(self):
        """Test that get_metrics_content_type returns a string."""
        from src.core.metrics import get_metrics_content_type
        content_type = get_metrics_content_type()
        assert isinstance(content_type, str)
        assert "text/plain" in content_type
    
    def test_get_metrics_contains_prometheus_format(self):
        """Test that get_metrics returns valid Prometheus format."""
        from src.core.metrics import get_metrics
        result = get_metrics().decode("utf-8")
        # Prometheus format starts with # HELP or # TYPE
        assert "# HELP" in result or "# TYPE" in result
    
    def test_get_metrics_contains_tool_metrics(self):
        """Test that get_metrics output contains tool metric names."""
        from src.core.metrics import get_metrics
        result = get_metrics().decode("utf-8")
        assert "confluence_mcp_tool_invocations_total" in result
        assert "confluence_mcp_tool_duration_seconds" in result
    
    def test_get_metrics_contains_server_metrics(self):
        """Test that get_metrics output contains server metric names."""
        from src.core.metrics import get_metrics
        result = get_metrics().decode("utf-8")
        assert "confluence_mcp_server_start_time_seconds" in result
        assert "confluence_mcp_server_uptime_seconds" in result


class TestToolMetrics:
    """Tests for tool invocation metrics."""
    
    def test_record_tool_invocation_success(self):
        """Test recording a successful tool invocation."""
        from src.core.metrics import record_tool_invocation, TOOL_INVOCATIONS
        
        # Get current count before
        before = TOOL_INVOCATIONS.labels(
            tool_name="test_tool_success", status="success"
        )._value.get()
        
        record_tool_invocation("test_tool_success", "success")
        
        after = TOOL_INVOCATIONS.labels(
            tool_name="test_tool_success", status="success"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_tool_invocation_error(self):
        """Test recording a failed tool invocation."""
        from src.core.metrics import record_tool_invocation, TOOL_INVOCATIONS
        
        before = TOOL_INVOCATIONS.labels(
            tool_name="test_tool_error", status="error"
        )._value.get()
        
        record_tool_invocation("test_tool_error", "error")
        
        after = TOOL_INVOCATIONS.labels(
            tool_name="test_tool_error", status="error"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_tool_duration(self):
        """Test recording tool execution duration."""
        from src.core.metrics import record_tool_duration, TOOL_DURATION
        
        # Get the sum before to verify it increases
        before_sum = TOOL_DURATION.labels(
            tool_name="test_duration_tool"
        )._sum.get()
        
        record_tool_duration("test_duration_tool", 0.5)
        
        after_sum = TOOL_DURATION.labels(
            tool_name="test_duration_tool"
        )._sum.get()
        
        # Sum should have increased by approximately 0.5
        assert after_sum >= before_sum + 0.4
    
    def test_record_tool_error(self):
        """Test recording a tool error."""
        from src.core.metrics import record_tool_error, TOOL_ERRORS
        
        before = TOOL_ERRORS.labels(
            tool_name="test_error_tool", error_type="ValueError"
        )._value.get()
        
        record_tool_error("test_error_tool", "ValueError")
        
        after = TOOL_ERRORS.labels(
            tool_name="test_error_tool", error_type="ValueError"
        )._value.get()
        
        assert after == before + 1


class TestHTTPMetrics:
    """Tests for HTTP request metrics."""
    
    def test_record_http_request(self):
        """Test recording an HTTP request."""
        from src.core.metrics import record_http_request, HTTP_REQUESTS
        
        before = HTTP_REQUESTS.labels(
            method="GET", endpoint="/metrics", status_code="200"
        )._value.get()
        
        record_http_request("GET", "/metrics", 200, 0.01)
        
        after = HTTP_REQUESTS.labels(
            method="GET", endpoint="/metrics", status_code="200"
        )._value.get()
        
        assert after == before + 1
    
    def test_record_http_request_duration(self):
        """Test recording HTTP request duration."""
        from src.core.metrics import record_http_request, HTTP_DURATION
        
        before_sum = HTTP_DURATION.labels(
            method="GET", endpoint="/health"
        )._sum.get()
        
        record_http_request("GET", "/health", 200, 0.05)
        
        after_sum = HTTP_DURATION.labels(
            method="GET", endpoint="/health"
        )._sum.get()
        
        # Sum should have increased by approximately 0.05
        assert after_sum >= before_sum + 0.04


class TestServerMetrics:
    """Tests for server-level metrics."""
    
    def test_server_start_time_is_set(self):
        """Test that server start time is set when module is imported."""
        from src.core.metrics import SERVER_START_TIME
        
        # Server start time should be set (non-zero)
        start_time = SERVER_START_TIME._value.get()
        assert start_time > 0
    
    def test_set_server_start_time(self):
        """Test setting server start time."""
        from src.core.metrics import set_server_start_time, SERVER_START_TIME
        
        before = time.time()
        set_server_start_time()
        after = time.time()
        
        start_time = SERVER_START_TIME._value.get()
        assert before <= start_time <= after
    
    def test_update_server_uptime(self):
        """Test updating server uptime."""
        from src.core.metrics import update_server_uptime, SERVER_UPTIME
        
        before = time.time()
        update_server_uptime()
        after = time.time()
        
        uptime = SERVER_UPTIME._value.get()
        assert before <= uptime <= after
    
    def test_active_connections_increment(self):
        """Test incrementing active connections."""
        from src.core.metrics import increment_active_connections, ACTIVE_CONNECTIONS
        
        before = ACTIVE_CONNECTIONS._value.get()
        increment_active_connections()
        after = ACTIVE_CONNECTIONS._value.get()
        
        assert after == before + 1
    
    def test_active_connections_decrement(self):
        """Test decrementing active connections."""
        from src.core.metrics import (
            increment_active_connections,
            decrement_active_connections,
            ACTIVE_CONNECTIONS
        )
        
        # First increment to ensure we can decrement
        increment_active_connections()
        before = ACTIVE_CONNECTIONS._value.get()
        
        decrement_active_connections()
        after = ACTIVE_CONNECTIONS._value.get()
        
        assert after == before - 1


class TestInstrumentToolDecorator:
    """Tests for the instrument_tool decorator."""
    
    def test_instrument_tool_success(self):
        """Test that instrument_tool decorator records success metrics."""
        from src.core.metrics import instrument_tool, TOOL_INVOCATIONS, TOOL_DURATION
        
        @instrument_tool("decorated_tool")
        def my_tool():
            return "result"
        
        before_invocations = TOOL_INVOCATIONS.labels(
            tool_name="decorated_tool", status="success"
        )._value.get()
        before_duration_sum = TOOL_DURATION.labels(
            tool_name="decorated_tool"
        )._sum.get()
        
        result = my_tool()
        
        assert result == "result"
        
        after_invocations = TOOL_INVOCATIONS.labels(
            tool_name="decorated_tool", status="success"
        )._value.get()
        after_duration_sum = TOOL_DURATION.labels(
            tool_name="decorated_tool"
        )._sum.get()
        
        assert after_invocations == before_invocations + 1
        # Duration sum should have increased (even if very small)
        assert after_duration_sum >= before_duration_sum
    
    def test_instrument_tool_error(self):
        """Test that instrument_tool decorator records error metrics."""
        from src.core.metrics import instrument_tool, TOOL_INVOCATIONS, TOOL_ERRORS
        
        @instrument_tool("error_tool")
        def failing_tool():
            raise ValueError("Test error")
        
        before_errors = TOOL_INVOCATIONS.labels(
            tool_name="error_tool", status="error"
        )._value.get()
        before_error_count = TOOL_ERRORS.labels(
            tool_name="error_tool", error_type="ValueError"
        )._value.get()
        
        with pytest.raises(ValueError):
            failing_tool()
        
        after_errors = TOOL_INVOCATIONS.labels(
            tool_name="error_tool", status="error"
        )._value.get()
        after_error_count = TOOL_ERRORS.labels(
            tool_name="error_tool", error_type="ValueError"
        )._value.get()
        
        assert after_errors == before_errors + 1
        assert after_error_count == before_error_count + 1
    
    def test_instrument_tool_uses_function_name_by_default(self):
        """Test that instrument_tool uses function name when no name provided."""
        from src.core.metrics import instrument_tool, TOOL_INVOCATIONS
        
        @instrument_tool()
        def my_named_function():
            return "result"
        
        before = TOOL_INVOCATIONS.labels(
            tool_name="my_named_function", status="success"
        )._value.get()
        
        my_named_function()
        
        after = TOOL_INVOCATIONS.labels(
            tool_name="my_named_function", status="success"
        )._value.get()
        
        assert after == before + 1
    
    def test_instrument_tool_preserves_function_metadata(self):
        """Test that instrument_tool preserves function name and docstring."""
        from src.core.metrics import instrument_tool
        
        @instrument_tool("test_preserve")
        def my_function():
            """My function docstring."""
            return "result"
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring."


class TestMetricsEndpointIntegration:
    """Integration tests for the /metrics endpoint in SSE mode."""
    
    def test_metrics_endpoint_returns_prometheus_format(self):
        """Test that the /metrics endpoint returns Prometheus format data."""
        from src.core.metrics import get_metrics, get_metrics_content_type
        
        content = get_metrics()
        content_type = get_metrics_content_type()
        
        assert isinstance(content, bytes)
        assert "text/plain" in content_type
        
        # Decode and check format
        text = content.decode("utf-8")
        assert "confluence_mcp" in text
    
    def test_metrics_endpoint_includes_all_metric_families(self):
        """Test that metrics output includes all defined metric families."""
        from src.core.metrics import get_metrics
        
        text = get_metrics().decode("utf-8")
        
        expected_metrics = [
            "confluence_mcp_tool_invocations_total",
            "confluence_mcp_tool_duration_seconds",
            "confluence_mcp_tool_errors_total",
            "confluence_mcp_http_requests_total",
            "confluence_mcp_http_request_duration_seconds",
            "confluence_mcp_server_start_time_seconds",
            "confluence_mcp_server_uptime_seconds",
            "confluence_mcp_active_connections",
        ]
        
        for metric in expected_metrics:
            assert metric in text, f"Expected metric '{metric}' not found in output"
