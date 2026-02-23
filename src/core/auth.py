"""Authentication and authorization module."""
from typing import Optional
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from enum import Enum

from src.core.config import Config


class UserRole(Enum):
    """User roles for access control."""
    READER = "reader"
    WRITER = "writer"
    ADMIN = "admin"


class AccessControl:
    """Access control manager for tool authorization."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def check_permission(self, role: UserRole, tool_name: str) -> bool:
        """Check if a role has permission to use a tool."""
        permissions = {
            "reader": ["search_confluence", "get_page_content", "list_pages", "health_check"],
            "writer": ["search_confluence", "get_page_content", "list_pages", "health_check"],
            "admin": ["*"],  # All tools
        }
        
        allowed_tools = permissions.get(role.value, [])
        return "*" in allowed_tools or tool_name in allowed_tools


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key authentication."""
    
    def __init__(self, app, config: Config):
        super().__init__(app)
        self.config = config
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for health endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # Require API key if configured
        if self.config.mcp_api_key:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != self.config.mcp_api_key:
                from starlette.responses import JSONResponse
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing API key"}
                )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
