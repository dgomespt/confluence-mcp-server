"""STDIO transport mode for Confluence MCP Server."""
import os

from src.core.logging_config import get_logger, setup_logging
from src.modules.confluence import create_mcp_app


# Initialize logger
logger = get_logger("stdio_mode")


def run_stdio():
    """Run the MCP server in STDIO mode."""
    # Setup logging
    structured = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
    setup_logging(structured=structured)
    
    logger.info("Starting Confluence MCP Server in STDIO mode")
    
    mcp = create_mcp_app(include_metrics=False)
    mcp.run()


if __name__ == "__main__":
    run_stdio()
