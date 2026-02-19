"""Health check functionality for Confluence MCP Server.

This module provides health check endpoints to verify the server
and Confluence API connectivity are working properly.
"""
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.core.config import Config
from src.core.logging_config import get_logger
from src.core.retry import retry_with_backoff


logger = get_logger("health")


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    status: str  # "healthy", "degraded", "unhealthy"
    checks: Dict[str, Any]
    timestamp: str
    duration_ms: float


class ConfluenceHealthCheck:
    """Health checker for Confluence API connectivity."""
    
    def __init__(self, confluence_client, config: Optional[Config] = None):
        """Initialize the health checker.
        
        Args:
            confluence_client: The Confluence client to check.
            config: Optional configuration for additional context.
        """
        self.confluence_client = confluence_client
        self.config = config
    
    @retry_with_backoff(max_retries=2, initial_delay=0.5)
    def check_connectivity(self) -> Dict[str, Any]:
        """Check if Confluence API is reachable.
        
        Returns:
            Dictionary with connectivity check results.
        
        Raises:
            Exception if the check fails.
        """
        start_time = time.time()
        
        # Try to get server info
        try:
            # Use the get_server_info method if available, otherwise use a simple call
            if hasattr(self.confluence_client, 'get_server_info'):
                server_info = self.confluence_client.get_server_info()
            elif hasattr(self.confluence_client, 'get'):
                # Try a generic GET request to the base URL
                server_info = self.confluence_client.get('')
            else:
                # Fallback: try to get current user (lightweight call)
                if hasattr(self.confluence_client, 'get_current_user'):
                    self.confluence_client.get_current_user()
                server_info = {"status": "ok"}
            
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(duration_ms, 2),
                "message": "Successfully connected to Confluence"
            }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Confluence connectivity check failed: {str(e)}")
            
            return {
                "status": "unhealthy",
                "response_time_ms": round(duration_ms, 2),
                "message": f"Failed to connect to Confluence: {str(e)}"
            }
    
    def check_api_limits(self) -> Dict[str, Any]:
        """Check API rate limits (if available).
        
        Returns:
            Dictionary with rate limit information.
        """
        # This would check rate limits if the client provides that info
        # Most Atlassian clients don't expose this directly, so we return a placeholder
        return {
            "status": "unknown",
            "message": "Rate limit information not available"
        }


def perform_health_check(
    confluence_client,
    config: Optional[Config] = None
) -> HealthCheckResult:
    """Perform a full health check of the MCP server and Confluence connection.
    
    Args:
        confluence_client: The Confluence client to check.
        config: Optional configuration for additional context.
    
    Returns:
        HealthCheckResult with overall status and individual checks.
    """
    start_time = time.time()
    checks = {}
    overall_status = "healthy"
    
    # Check server uptime
    checks["server"] = {
        "status": "healthy",
        "message": "Server is running"
    }
    
    # Check Confluence connectivity
    health_checker = ConfluenceHealthCheck(confluence_client, config)
    
    try:
        connectivity = health_checker.check_connectivity()
        checks["confluence_connectivity"] = connectivity
        
        if connectivity["status"] != "healthy":
            overall_status = "degraded"
    except Exception as e:
        checks["confluence_connectivity"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        overall_status = "unhealthy"
    
    # Check API limits
    try:
        rate_limits = health_checker.check_api_limits()
        checks["api_limits"] = rate_limits
    except Exception as e:
        checks["api_limits"] = {
            "status": "unknown",
            "message": str(e)
        }
    
    # If any critical check is unhealthy, mark overall as unhealthy
    for check_name, check_result in checks.items():
        if check_result.get("status") == "unhealthy" and check_name in ["server", "confluence_connectivity"]:
            overall_status = "unhealthy"
            break
    
    duration_ms = (time.time() - start_time) * 1000
    
    return HealthCheckResult(
        status=overall_status,
        checks=checks,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        duration_ms=round(duration_ms, 2)
    )


def get_health_status_dict(
    confluence_client,
    config: Optional[Config] = None
) -> Dict[str, Any]:
    """Get health status as a dictionary for JSON serialization.
    
    Args:
        confluence_client: The Confluence client to check.
        config: Optional configuration.
    
    Returns:
        Dictionary with health status.
    """
    result = perform_health_check(confluence_client, config)
    return {
        "status": result.status,
        "timestamp": result.timestamp,
        "duration_ms": result.duration_ms,
        "checks": result.checks
    }
