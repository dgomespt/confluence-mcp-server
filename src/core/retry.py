"""Retry logic with exponential backoff for Confluence MCP Server.

This module provides retry decorators and utilities for handling
transient failures when calling external APIs.
"""
import asyncio
import time
import functools
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union
from collections.abc import Collection

from src.core.exceptions import (
    ConfluenceAPIError,
    ConfluenceAuthenticationError,
    ConfluencePermissionError,
    ConfluenceNotFoundError,
    ConfluenceRateLimitError,
    MaxRetriesExceededError,
    RetryableError,
)
from src.core.logging_config import get_logger


# Type variable for function return type
F = TypeVar("F", bound=Callable[..., Any])

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 1.0  # seconds
DEFAULT_MAX_DELAY = 30.0  # seconds
DEFAULT_BACKOFF_FACTOR = 2.0


# Errors that should trigger a retry
RETRYABLE_ERROR_CODES = {429, 500, 502, 503, 504}


logger = get_logger("retry")


def is_retryable_error(exception: Exception) -> bool:
    """Determine if an exception is retryable.
    
    Args:
        exception: The exception to check.
    
    Returns:
        True if the error is retryable, False otherwise.
    """
    # Check if it's a known API error
    if isinstance(exception, ConfluenceAPIError):
        # Rate limit errors are always retryable
        if isinstance(exception, ConfluenceRateLimitError):
            return True
        # Server errors (5xx) are retryable
        if exception.status_code in RETRYABLE_ERROR_CODES:
            return True
        # Authentication and permission errors are not retryable
        if isinstance(exception, (ConfluenceAuthenticationError, ConfluencePermissionError)):
            return False
        # Other API errors might be transient
        return exception.status_code is not None and exception.status_code >= 500
    
    # Check for network-related errors
    error_message = str(exception).lower()
    retryable_patterns = [
        "connection",
        "timeout",
        "temporary failure",
        "service unavailable",
        "too many requests",
    ]
    
    if any(pattern in error_message for pattern in retryable_patterns):
        return True
    
    # Default: treat generic exceptions as retryable
    return True


def calculate_delay(
    attempt: int,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retry_after: Optional[int] = None
) -> float:
    """Calculate delay before next retry using exponential backoff.
    
    Args:
        attempt: The current retry attempt (0-indexed).
        initial_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        backoff_factor: Multiplier for each subsequent delay.
        retry_after: Optional retry-after value from rate limit response.
    
    Returns:
        Delay in seconds before next retry.
    """
    # If we have a retry-after header, use it
    if retry_after is not None:
        return min(retry_after, max_delay)
    
    # Otherwise, calculate exponential backoff with jitter
    delay = initial_delay * (backoff_factor ** attempt)
    
    # Add small random jitter (0-1 second)
    import secrets
    jitter = secrets.SystemRandom().random()
    
    return min(delay + jitter, max_delay)


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retryable_errors: Optional[Collection[Type[Exception]]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[F], F]:
    """Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay in seconds between retries.
        backoff_factor: Multiplier for each subsequent delay.
        retryable_errors: Collection of exception types to retry on.
                         If None, uses is_retryable_error() logic.
        on_retry: Optional callback function called before each retry.
                 Takes (exception, attempt_number) as arguments.
    
    Returns:
        Decorated function that retries on failure.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt >= max_retries:
                        break
                    
                    # Determine if this error is retryable
                    should_retry = False
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = is_retryable_error(e)
                    
                    if not should_retry:
                        # Non-retryable error, raise immediately
                        raise
                    
                    # Calculate delay
                    retry_after = None
                    if isinstance(e, ConfluenceRateLimitError):
                        retry_after = e.retry_after
                    
                    delay = calculate_delay(
                        attempt=attempt,
                        initial_delay=initial_delay,
                        max_delay=max_delay,
                        backoff_factor=backoff_factor,
                        retry_after=retry_after
                    )
                    
                    # Log the retry
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # All retries exhausted
            logger.error(
                f"Max retries ({max_retries}) exceeded for {func.__name__}. "
                f"Last error: {str(last_exception)}"
            )
            raise MaxRetriesExceededError(
                message=f"Max retries ({max_retries}) exceeded for {func.__name__}",
                total_retries=max_retries,
                last_exception=last_exception
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt >= max_retries:
                        break
                    
                    # Determine if this error is retryable
                    should_retry = False
                    if retryable_errors:
                        should_retry = isinstance(e, retryable_errors)
                    else:
                        should_retry = is_retryable_error(e)
                    
                    if not should_retry:
                        raise
                    
                    # Calculate delay
                    retry_after = None
                    if isinstance(e, ConfluenceRateLimitError):
                        retry_after = e.retry_after
                    
                    delay = calculate_delay(
                        attempt=attempt,
                        initial_delay=initial_delay,
                        max_delay=max_delay,
                        backoff_factor=backoff_factor,
                        retry_after=retry_after
                    )
                    
                    # Log the retry
                    logger.warning(
                        f"Async retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retrying
                    await asyncio.sleep(delay)
            
            # All retries exhausted
            raise MaxRetriesExceededError(
                message=f"Max retries ({max_retries}) exceeded for {func.__name__}",
                total_retries=max_retries,
                last_exception=last_exception
            )
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore
    
    return decorator


def retry_on_predicate(
    predicate: Callable[[Exception], bool],
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
) -> Callable[[F], F]:
    """Decorator to retry a function based on a predicate.
    
    Args:
        predicate: Function that takes an exception and returns True
                  if the function should be retried.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay in seconds between retries.
        backoff_factor: Multiplier for each subsequent delay.
    
    Returns:
        Decorated function that retries based on predicate.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt >= max_retries or not predicate(e):
                        raise
                    
                    # Calculate delay
                    delay = calculate_delay(
                        attempt=attempt,
                        initial_delay=initial_delay,
                        max_delay=max_delay,
                        backoff_factor=backoff_factor
                    )
                    
                    # Log the retry
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            raise MaxRetriesExceededError(
                message=f"Max retries ({max_retries}) exceeded for {func.__name__}",
                total_retries=max_retries,
                last_exception=last_exception
            )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt >= max_retries or not predicate(e):
                        raise
                    
                    delay = calculate_delay(
                        attempt=attempt,
                        initial_delay=initial_delay,
                        max_delay=max_delay,
                        backoff_factor=backoff_factor
                    )
                    
                    logger.warning(
                        f"Async retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
            
            raise MaxRetriesExceededError(
                message=f"Max retries ({max_retries}) exceeded for {func.__name__}",
                total_retries=max_retries,
                last_exception=last_exception
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return wrapper  # type: ignore
    
    return decorator
