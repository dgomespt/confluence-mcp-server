"""Input validation for Confluence MCP Server.

This module provides validation functions for tool parameters
to ensure data integrity and prevent errors.
"""
import re
from typing import Any, Optional, Tuple

from src.core.exceptions import (
    InvalidLimitError,
    InvalidPageIdError,
    InvalidQueryError,
    InvalidSpaceKeyError,
    ValidationError,
)


# Validation constants
MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10

MIN_QUERY_LENGTH = 1
MAX_QUERY_LENGTH = 500

MIN_SPACE_KEY_LENGTH = 1
MAX_SPACE_KEY_LENGTH = 10

# Valid page ID patterns (alphanumeric, hyphens, underscores)
PAGE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Valid space key pattern (uppercase letters, numbers, possibly with hyphen)
SPACE_KEY_PATTERN = re.compile(r"^[A-Z0-9]+(-[A-Z0-9]+)?$")


def validate_query(query: str) -> str:
    """Validate search query string.
    
    Args:
        query: The search query to validate.
    
    Returns:
        The validated query string.
    
    Raises:
        InvalidQueryError: If query is invalid.
    """
    # Check for None or empty
    if not query:
        raise InvalidQueryError(query or "", "Query cannot be empty")
    
    # Check minimum length
    if len(query) < MIN_QUERY_LENGTH:
        raise InvalidQueryError(
            query,
            f"Query must be at least {MIN_QUERY_LENGTH} characters"
        )
    
    # Check maximum length
    if len(query) > MAX_QUERY_LENGTH:
        raise InvalidQueryError(
            query,
            f"Query must be at most {MAX_QUERY_LENGTH} characters"
        )
    
    # Check for only whitespace
    if not query.strip():
        raise InvalidQueryError(query, "Query cannot be only whitespace")
    
    return query.strip()


def validate_page_id(page_id: str) -> str:
    """Validate page ID string.
    
    Args:
        page_id: The page ID to validate.
    
    Returns:
        The validated page ID string.
    
    Raises:
        InvalidPageIdError: If page_id is invalid.
    """
    # Check for None or empty
    if not page_id:
        raise InvalidPageIdError(page_id or "")
    
    # Strip whitespace
    page_id = page_id.strip()
    
    # Check minimum length
    if len(page_id) < 1:
        raise InvalidPageIdError(page_id)
    
    # Check pattern (alphanumeric, hyphens, underscores)
    if not PAGE_ID_PATTERN.match(page_id):
        raise InvalidPageIdError(
            page_id,
        )
    
    return page_id


def validate_space_key(space: str) -> str:
    """Validate Confluence space key.
    
    Args:
        space: The space key to validate.
    
    Returns:
        The validated space key string.
    
    Raises:
        InvalidSpaceKeyError: If space key is invalid.
    """
    # Check for None or empty
    if not space:
        raise InvalidSpaceKeyError(space or "")
    
    # Strip whitespace
    space = space.strip().upper()
    
    # Check minimum length
    if len(space) < MIN_SPACE_KEY_LENGTH:
        raise InvalidSpaceKeyError(space)
    
    # Check maximum length
    if len(space) > MAX_SPACE_KEY_LENGTH:
        raise InvalidSpaceKeyError(
            space,
        )
    
    # Check pattern (uppercase letters, numbers, possibly with hyphen)
    if not SPACE_KEY_PATTERN.match(space):
        raise InvalidSpaceKeyError(
            space,
        )
    
    return space


def validate_limit(limit: int, min_val: int = MIN_LIMIT, max_val: int = MAX_LIMIT) -> int:
    """Validate limit parameter.
    
    Args:
        limit: The limit value to validate.
        min_val: Minimum allowed value (default: MIN_LIMIT).
        max_val: Maximum allowed value (default: MAX_LIMIT).
    
    Returns:
        The validated limit value.
    
    Raises:
        InvalidLimitError: If limit is invalid.
    """
    # Check type
    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise InvalidLimitError(limit, min_val, max_val)
    
    # Check range
    if limit < min_val or limit > max_val:
        raise InvalidLimitError(limit, min_val, max_val)
    
    return limit


def validate_boolean(value: Any, field_name: str = "value", default: bool = True) -> bool:
    """Validate boolean parameter.
    
    Args:
        value: The value to validate.
        field_name: Name of the field for error messages.
        default: Default value if value is None.
    
    Returns:
        The validated boolean value.
    
    Raises:
        ValidationError: If value cannot be converted to boolean.
    """
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ("true", "1", "yes", "on"):
            return True
        if value_lower in ("false", "0", "no", "off"):
            return False
    
    raise ValidationError(
        message=f"Invalid boolean value for {field_name}: {value}",
        field=field_name,
        value=value
    )


def sanitize_string(
    value: str,
    max_length: Optional[int] = None,
    strip_html: bool = False,
    field_name: str = "value"
) -> str:
    """Sanitize a string value.
    
    Args:
        value: The string to sanitize.
        max_length: Optional maximum length.
        strip_html: Whether to strip HTML tags.
        field_name: Name of the field for error messages.
    
    Returns:
        The sanitized string.
    
    Raises:
        ValidationError: If value is not a valid string.
    """
    if value is None:
        return ""
    
    if not isinstance(value, str):
        raise ValidationError(
            message=f"Expected string for {field_name}",
            field=field_name,
            value=value
        )
    
    # Strip whitespace
    value = value.strip()
    
    # Strip HTML if requested
    if strip_html:
        # Simple HTML tag removal
        value = re.sub(r"<[^>]+>", "", value)
    
    # Truncate if too long
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_and_sanitize_search_params(
    query: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[str, int]:
    """Validate and sanitize search parameters.
    
    Args:
        query: Search query string.
        limit: Maximum number of results.
    
    Returns:
        Tuple of (validated_query, validated_limit).
    
    Raises:
        InvalidQueryError: If query is invalid.
        InvalidLimitError: If limit is invalid.
    """
    validated_query = validate_query(query) if query else ""
    validated_limit = validate_limit(limit) if limit else DEFAULT_LIMIT
    
    return validated_query, validated_limit


def validate_and_sanitize_page_params(
    page_id: Optional[str] = None,
    convert_to_markdown: Optional[bool] = None,
) -> Tuple[str, bool]:
    """Validate and sanitize page parameters.
    
    Args:
        page_id: Page ID string.
        convert_to_markdown: Whether to convert to markdown.
    
    Returns:
        Tuple of (validated_page_id, validated_convert_to_markdown).
    
    Raises:
        InvalidPageIdError: If page_id is invalid.
    """
    validated_page_id = validate_page_id(page_id) if page_id else ""
    validated_convert = validate_boolean(convert_to_markdown, "convert_to_markdown")
    
    return validated_page_id, validated_convert


def validate_and_sanitize_list_params(
    space: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[str, int]:
    """Validate and sanitize list pages parameters.
    
    Args:
        space: Space key string.
        limit: Maximum number of results.
    
    Returns:
        Tuple of (validated_space, validated_limit).
    
    Raises:
        InvalidSpaceKeyError: If space is invalid.
        InvalidLimitError: If limit is invalid.
    """
    validated_space = validate_space_key(space) if space else "ENG"
    validated_limit = validate_limit(limit) if limit else DEFAULT_LIMIT
    
    return validated_space, validated_limit
