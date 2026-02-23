"""Tests for authentication and authorization module."""
import pytest
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route

from src.core.auth import ApiKeyMiddleware, SecurityHeadersMiddleware, UserRole, AccessControl
from src.core.config import Config


def test_security_headers_middleware():
    """Test that security headers are added to responses."""
    async def test_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"test": "data"})
    
    app = Starlette(routes=[Route("/test", endpoint=test_endpoint)])
    app.add_middleware(SecurityHeadersMiddleware)
    
    client = TestClient(app)
    
    response = client.get("/test")
    
    assert response.status_code == 200
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-XSS-Protection" in response.headers
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Referrer-Policy" in response.headers
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_api_key_middleware_with_valid_key():
    """Test API key authentication with valid key."""
    async def test_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"test": "data"})
    
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token",
        mcp_api_key="test-api-key"
    )
    
    app = Starlette(routes=[Route("/test", endpoint=test_endpoint)])
    app.add_middleware(ApiKeyMiddleware, config=config)
    
    client = TestClient(app)
    
    response = client.get("/test", headers={"X-API-Key": "test-api-key"})
    
    assert response.status_code == 200
    assert response.json() == {"test": "data"}


def test_api_key_middleware_missing_key():
    """Test API key authentication with missing key."""
    async def test_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"test": "data"})
    
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token",
        mcp_api_key="test-api-key"
    )
    
    app = Starlette(routes=[Route("/test", endpoint=test_endpoint)])
    app.add_middleware(ApiKeyMiddleware, config=config)
    
    client = TestClient(app)
    
    response = client.get("/test")
    
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_api_key_middleware_invalid_key():
    """Test API key authentication with invalid key."""
    async def test_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"test": "data"})
    
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token",
        mcp_api_key="test-api-key"
    )
    
    app = Starlette(routes=[Route("/test", endpoint=test_endpoint)])
    app.add_middleware(ApiKeyMiddleware, config=config)
    
    client = TestClient(app)
    
    response = client.get("/test", headers={"X-API-Key": "invalid-key"})
    
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_api_key_middleware_disabled_when_no_key_configured():
    """Test that API key authentication is disabled when no key is configured."""
    async def test_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({"test": "data"})
    
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token"
    )
    
    app = Starlette(routes=[Route("/test", endpoint=test_endpoint)])
    app.add_middleware(ApiKeyMiddleware, config=config)
    
    client = TestClient(app)
    
    response = client.get("/test")
    
    assert response.status_code == 200
    assert response.json() == {"test": "data"}


def test_access_control_reader_role():
    """Test access control for reader role."""
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token"
    )
    
    access_control = AccessControl(config)
    
    assert access_control.check_permission(UserRole.READER, "search_confluence") is True
    assert access_control.check_permission(UserRole.READER, "get_page_content") is True
    assert access_control.check_permission(UserRole.READER, "list_pages") is True
    assert access_control.check_permission(UserRole.READER, "health_check") is True


def test_access_control_admin_role():
    """Test access control for admin role (should have all permissions)."""
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token"
    )
    
    access_control = AccessControl(config)
    
    assert access_control.check_permission(UserRole.ADMIN, "search_confluence") is True
    assert access_control.check_permission(UserRole.ADMIN, "nonexistent_tool") is True


def test_access_control_disallowed_tool():
    """Test access control for disallowed tool."""
    config = Config(
        confluence_url="https://test.atlassian.net",
        confluence_username="test@example.com",
        confluence_api_token="test-token"
    )
    
    access_control = AccessControl(config)
    
    assert access_control.check_permission(UserRole.READER, "admin_tool") is False
