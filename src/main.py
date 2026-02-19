"""Main entry point for Confluence MCP Server.

This module provides a unified entry point that can run the server
in either STDIO or SSE mode based on configuration.
"""
import os
import sys

from src.core.config import Config
from src.core.logging_config import setup_logging, get_logger


# Initialize logger
logger = get_logger("main")


def main():
    """Main entry point for the Confluence MCP Server."""
    # Setup logging based on environment
    structured = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(level=log_level, structured=structured)
    
    # Get transport mode from environment or CLI argument
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    
    logger.info(f"Starting Confluence MCP Server in {transport.upper()} mode")
    
    if transport == "sse":
        # Run in SSE mode
        from src.transports.sse_mode import run_sse
        
        config = Config.from_env_optional()
        host = config.host if config else "0.0.0.0"
        port = config.port if config else 8080
        
        logger.info(f"Starting SSE server on {host}:{port}")
        print(f"Starting Confluence MCP Server in SSE mode on {host}:{port}", file=sys.stderr)
        run_sse(host=host, port=port)
    else:
        # Run in STDIO mode (default)
        from src.transports.stdio_mode import run_stdio
        
        logger.info("Starting STDIO server")
        print("Starting Confluence MCP Server in STDIO mode", file=sys.stderr)
        run_stdio()


if __name__ == "__main__":
    main()
