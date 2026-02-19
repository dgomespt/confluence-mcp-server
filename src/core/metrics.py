"""Prometheus metrics for Confluence MCP Server.

This module provides Prometheus metrics to monitor the MCP server's
performance, tool invocations, and error rates.
"""
import time
from functools import wraps
from typing import Callable, Optional

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from src.core.logging_config import get_logger


logger = get_logger("metrics")

# ============================================
# Tool Metrics
# ============================================

# Counter for tool invocations by tool name and status
TOOL_INVOCATIONS = Counter(
    "confluence_mcp_tool_invocations_total",
    "Total number of tool invocations",
    ["tool_name", "status"]
)

# Histogram for tool execution duration in seconds
TOOL_DURATION = Histogram(
    "confluence_mcp_tool_duration_seconds",
    "Tool execution duration in seconds",
    ["tool_name"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Counter for tool errors by tool name and error type
TOOL_ERRORS = Counter(
    "confluence_mcp_tool_errors_total",
    "Total number of tool errors",
    ["tool_name", "error_type"]
)

# ============================================
# HTTP Server Metrics
# ============================================

# Counter for HTTP requests by method, endpoint, and status code
HTTP_REQUESTS = Counter(
    "confluence_mcp_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

# Histogram for HTTP request duration in seconds
HTTP_DURATION = Histogram(
    "confluence_mcp_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# ============================================
# Server Metrics
# ============================================

# Gauge for server start time (Unix timestamp)
SERVER_START_TIME = Gauge(
    "confluence_mcp_server_start_time_seconds",
    "Server start time in Unix seconds"
)

# Gauge for server uptime in seconds
SERVER_UPTIME = Gauge(
    "confluence_mcp_server_uptime_seconds",
    "Server uptime in seconds"
)

# Gauge for current number of active connections
ACTIVE_CONNECTIONS = Gauge(
    "confluence_mcp_active_connections",
    "Number of active SSE connections"
)


def record_tool_invocation(tool_name: str, status: str = "success"):
    """Record a tool invocation.
    
    Args:
        tool_name: Name of the tool being invoked.
        status: Status of the invocation ("success" or "error").
    """
    TOOL_INVOCATIONS.labels(tool_name=tool_name, status=status).inc()


def record_tool_duration(tool_name: str, duration: float):
    """Record tool execution duration.
    
    Args:
        tool_name: Name of the tool.
        duration: Execution duration in seconds.
    """
    TOOL_DURATION.labels(tool_name=tool_name).observe(duration)


def record_tool_error(tool_name: str, error_type: str):
    """Record a tool error.
    
    Args:
        tool_name: Name of the tool that errored.
        error_type: Type/class of the error.
    """
    TOOL_ERRORS.labels(tool_name=tool_name, error_type=error_type).inc()


def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record an HTTP request.
    
    Args:
        method: HTTP method (GET, POST, etc.).
        endpoint: Request endpoint/path.
        status_code: HTTP response status code.
        duration: Request duration in seconds.
    """
    HTTP_REQUESTS.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
    HTTP_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def set_server_start_time():
    """Set the server start time."""
    SERVER_START_TIME.set(time.time())


def update_server_uptime():
    """Update the server uptime gauge."""
    SERVER_UPTIME.set(time.time())


def increment_active_connections():
    """Increment the active connections counter."""
    ACTIVE_CONNECTIONS.inc()


def decrement_active_connections():
    """Decrement the active connections counter."""
    ACTIVE_CONNECTIONS.dec()


def get_metrics() -> bytes:
    """Generate Prometheus metrics in text format.
    
    Returns:
        Prometheus metrics in text format.
    """
    # Update uptime before generating metrics
    update_server_uptime()
    return generate_latest()


def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics.
    
    Returns:
        Content type string for Prometheus metrics.
    """
    return CONTENT_TYPE_LATEST


def instrument_tool(tool_name: Optional[str] = None) -> Callable:
    """Decorator to instrument a tool function with metrics.
    
    Args:
        tool_name: Optional name override. Defaults to function name.
    
    Returns:
        Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = tool_name or func.__name__
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                record_tool_invocation(name, "success")
                return result
            except Exception as e:
                record_tool_invocation(name, "error")
                record_tool_error(name, type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                record_tool_duration(name, duration)
        return wrapper
    return decorator


# Initialize server start time when module is imported
set_server_start_time()
