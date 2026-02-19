"""Configuration module for Confluence MCP Server."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for the Confluence MCP Server."""
    
    confluence_url: str
    confluence_username: str
    confluence_api_token: str
    transport: str = "stdio"
    host: str = "0.0.0.0"
    port: int = 8080
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            confluence_url=cls._require_env("CONFLUENCE_URL"),
            confluence_username=cls._require_env("CONFLUENCE_USERNAME"),
            confluence_api_token=cls._require_env("CONFLUENCE_API_TOKEN"),
            transport=os.getenv("MCP_TRANSPORT", "stdio"),
            host=os.getenv("MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("MCP_PORT", "8080")),
        )
    
    @staticmethod
    def _require_env(key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @classmethod
    def from_env_optional(cls) -> Optional["Config"]:
        """Create configuration from environment variables (optional - returns None if not set)."""
        try:
            return cls.from_env()
        except ValueError:
            return None


def get_confluence_client(config: Config):
    """Create a Confluence client from configuration."""
    from atlassian import Confluence
    
    return Confluence(
        url=config.confluence_url,
        username=config.confluence_username,
        password=config.confluence_api_token,
        cloud=True  # Set to False for Data Center/On-Prem
    )
