"""SSE (Server-Sent Events) transport mode for Confluence MCP Server.

This transport mode allows the MCP server to run as a remote server
that clients can connect to via HTTP SSE.
"""
import os
from typing import Optional

import uvicorn

from src.core.logging_config import get_logger, setup_logging
from src.core.metrics import (
    get_metrics,
    get_metrics_content_type,
)
from src.modules.confluence import create_mcp_app


# Initialize logger
logger = get_logger("sse_mode")


def run_sse(host: str = "127.0.0.1", port: int = 8080):
    """Run the MCP server in SSE mode with metrics endpoint.
    
    Args:
        host: Host to bind to (default: 0.0.0.0).
        port: Port to bind to (default: 8080).
    """
    import anyio
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.requests import Request as StarletteRequest
    from starlette.responses import JSONResponse, Response as StarletteResponse
    
    # Setup logging
    structured = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
    setup_logging(structured=structured)
    
    logger.info(f"Starting Confluence MCP Server in SSE mode on {host}:{port}")
    
    # Create the MCP app with metrics enabled
    mcp = create_mcp_app(include_metrics=True)
    
    # Get the underlying SSE Starlette app from FastMCP
    mcp_sse_app = mcp.sse_app()
    
    # Define metrics and health endpoints
    async def metrics_endpoint(request: StarletteRequest) -> StarletteResponse:
        """Prometheus metrics endpoint."""
        return StarletteResponse(
            content=get_metrics(),
            media_type=get_metrics_content_type()
        )
    
    async def health_endpoint(request: StarletteRequest) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse({"status": "healthy"})
    
    # Create combined Starlette app with metrics and MCP routes
    app = Starlette(
        routes=[
            Route("/metrics", endpoint=metrics_endpoint, methods=["GET"]),
            Route("/health", endpoint=health_endpoint, methods=["GET"]),
            Mount("/", app=mcp_sse_app),
        ]
    )
    
    # Run with uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Confluence MCP Server - SSE Mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    run_sse(host=args.host, port=args.port)
