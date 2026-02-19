"""Custom exceptions for Confluence MCP Server.

This module defines custom exceptions that can be raised during
API operations, validation, and other server operations.
"""
from typing import Any, Dict, Optional


class ConfluenceMCPError(Exception):
    """Base exception for Confluence MCP Server errors.
    
    Attributes:
        message: Human-readable error message.
        code: Error code for programmatic error handling.
        details: Additional error details.
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }
    
    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"[{self.code}] {self.message} ({details_str})"
        return f"[{self.code}] {self.message}"


# API-related exceptions
class ConfluenceAPIError(ConfluenceMCPError):
    """Exception raised when Confluence API call fails.
    
    Attributes:
        status_code: HTTP status code from the API response.
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if status_code is not None:
            details["status_code"] = status_code
        if response is not None:
            details["response"] = response
        if code is not None:
            details["code"] = code
        
        super().__init__(
            message=message,
            code=code or "CONFLUENCE_API_ERROR",
            details=details
        )
        self.status_code = status_code
        self.response = response


class ConfluenceAuthenticationError(ConfluenceAPIError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            code="AUTHENTICATION_ERROR"
        )


class ConfluencePermissionError(ConfluenceAPIError):
    """Exception raised when user lacks permission."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            code="PERMISSION_ERROR"
        )


class ConfluenceNotFoundError(ConfluenceAPIError):
    """Exception raised when requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            status_code=404,
            code="NOT_FOUND_ERROR",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ConfluenceRateLimitError(ConfluenceAPIError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after}
        )
        self.retry_after = retry_after


# Validation exceptions
class ValidationError(ConfluenceMCPError):
    """Exception raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)[:100]  # Truncate long values
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )
        self.field = field
        self.value = value


class InvalidQueryError(ValidationError):
    """Exception raised when search query is invalid."""
    
    def __init__(self, query: str, reason: Optional[str] = None):
        message = f"Invalid search query: {query}"
        if reason:
            message += f" - {reason}"
        
        super().__init__(message=message, field="query", value=query)
        self.query = query
        self.reason = reason


class InvalidPageIdError(ValidationError):
    """Exception raised when page ID is invalid."""
    
    def __init__(self, page_id: str):
        super().__init__(
            message=f"Invalid page ID: {page_id}",
            field="page_id",
            value=page_id
        )
        self.page_id = page_id


class InvalidSpaceKeyError(ValidationError):
    """Exception raised when space key is invalid."""
    
    def __init__(self, space: str):
        super().__init__(
            message=f"Invalid space key: {space}",
            field="space",
            value=space
        )
        self.space = space


class InvalidLimitError(ValidationError):
    """Exception raised when limit parameter is invalid."""
    
    def __init__(self, limit: int, min_val: int = 1, max_val: int = 100):
        super().__init__(
            message=f"Invalid limit: {limit}. Must be between {min_val} and {max_val}",
            field="limit",
            value=limit
        )
        self.limit = limit
        self.min_val = min_val
        self.max_val = max_val


# Retry exceptions
class RetryableError(ConfluenceMCPError):
    """Exception raised when an operation can be retried."""
    
    def __init__(
        self,
        message: str,
        retry_count: int = 0,
        last_exception: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code="RETRYABLE_ERROR",
            details={
                "retry_count": retry_count,
                "last_exception": str(last_exception) if last_exception else None
            }
        )
        self.retry_count = retry_count
        self.last_exception = last_exception


class MaxRetriesExceededError(ConfluenceMCPError):
    """Exception raised when maximum retries have been exceeded."""
    
    def __init__(
        self,
        message: str,
        total_retries: int = 0,
        last_exception: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code="MAX_RETRIES_EXCEEDED",
            details={
                "total_retries": total_retries,
                "last_exception": str(last_exception) if last_exception else None
            }
        )
        self.total_retries = total_retries
        self.last_exception = last_exception


# Configuration exceptions
class ConfigurationError(ConfluenceMCPError):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, missing_field: Optional[str] = None):
        details = {}
        if missing_field:
            details["missing_field"] = missing_field
        
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details=details
        )
        self.missing_field = missing_field
