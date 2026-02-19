"""Error handling decorators for Confluence MCP Server.

This module provides decorators for handling errors from Confluence API calls,
converting them to user-friendly error messages and logging appropriately.
"""
import functools
import time
from typing import Any, Callable, Optional, TypeVar

from src.core.exceptions import (
    ConfluenceAPIError,
    ConfluenceAuthenticationError,
    ConfluenceNotFoundError,
    ConfluencePermissionError,
    ConfluenceRateLimitError,
    ConfluenceMCPError,
    MaxRetriesExceededError,
    RetryableError,
)
from src.core.logging_config import get_logger
from src.core.retry import retry_with_backoff, is_retryable_error


logger = get_logger("error_handling")


F = TypeVar("F", bound=Callable[..., Any])


def handle_api_errors(func: F) -> F:
    """Decorator to handle Confluence API errors.
    
    This decorator catches API errors and converts them to
    user-friendly error messages. It also logs errors appropriately.
    
    Args:
        func: The function to decorate.
    
    Returns:
        Decorated function with error handling.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ConfluenceNotFoundError as e:
            logger.warning(f"Resource not found: {e.message}")
            return f"Error: {e.message}"
        except ConfluenceAuthenticationError as e:
            logger.error(f"Authentication error: {e.message}")
            return f"Error: Authentication failed. Please check your credentials."
        except ConfluencePermissionError as e:
            logger.warning(f"Permission denied: {e.message}")
            return f"Error: Permission denied. You don't have access to this resource."
        except ConfluenceRateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e.message}")
            if e.retry_after:
                return f"Error: Rate limit exceeded. Please try again in {e.retry_after} seconds."
            return f"Error: Rate limit exceeded. Please try again later."
        except ConfluenceAPIError as e:
            logger.error(f"API error: {e.message}")
            return f"Error: {e.message}"
        except ConfluenceMCPError as e:
            logger.error(f"Confluence MCP error: {e.message}")
            return f"Error: {e.message}"
        except MaxRetriesExceededError as e:
            logger.error(f"Max retries exceeded: {e.message}")
            return f"Error: Operation failed after multiple attempts. Please try again later."
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return f"Error: An unexpected error occurred: {str(e)}"
    
    return wrapper  # type: ignore


def handle_api_errors_async(func: F) -> F:
    """Async version of handle_api_errors decorator.
    
    Args:
        func: The async function to decorate.
    
    Returns:
        Decorated async function with error handling.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ConfluenceNotFoundError as e:
            logger.warning(f"Resource not found: {e.message}")
            return f"Error: {e.message}"
        except ConfluenceAuthenticationError as e:
            logger.error(f"Authentication error: {e.message}")
            return f"Error: Authentication failed. Please check your credentials."
        except ConfluencePermissionError as e:
            logger.warning(f"Permission denied: {e.message}")
            return f"Error: Permission denied. You don't have access to this resource."
        except ConfluenceRateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e.message}")
            if e.retry_after:
                return f"Error: Rate limit exceeded. Please try again in {e.retry_after} seconds."
            return f"Error: Rate limit exceeded. Please try again later."
        except ConfluenceAPIError as e:
            logger.error(f"API error: {e.message}")
            return f"Error: {e.message}"
        except ConfluenceMCPError as e:
            logger.error(f"Confluence MCP error: {e.message}")
            return f"Error: {e.message}"
        except MaxRetriesExceededError as e:
            logger.error(f"Max retries exceeded: {e.message}")
            return f"Error: Operation failed after multiple attempts. Please try again later."
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return f"Error: An unexpected error occurred: {str(e)}"
    
    return wrapper  # type: ignore


def log_api_call(func: F) -> F:
    """Decorator to log API calls with timing.
    
    Args:
        func: The function to decorate.
    
    Returns:
        Decorated function with logging.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__
        
        logger.debug(f"Starting {func_name}")
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Completed {func_name} in {duration_ms:.2f}ms")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed {func_name} after {duration_ms:.2f}ms: {str(e)}")
            raise
    
    return wrapper  # type: ignore


def log_api_call_async(func: F) -> F:
    """Async version of log_api_call decorator.
    
    Args:
        func: The async function to decorate.
    
    Returns:
        Decorated async function with logging.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__
        
        logger.debug(f"Starting {func_name}")
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Completed {func_name} in {duration_ms:.2f}ms")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed {func_name} after {duration_ms:.2f}ms: {str(e)}")
            raise
    
    return wrapper  # type: ignore


def api_call_with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
) -> Callable[[F], F]:
    """Decorator to add retry logic to API calls.
    
    This combines retry logic with error handling to provide
    robust API call handling.
    
    Args:
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        backoff_factor: Exponential backoff multiplier.
    
    Returns:
        Decorator function.
    """
    def decorator(func: F) -> F:
        # Apply retry decorator
        retry_decorated = retry_with_backoff(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_factor=backoff_factor,
        )(func)
        
        # Apply error handling and logging
        return handle_api_errors(log_api_call(retry_decorated))  # type: ignore
    
    return decorator


def api_call_with_retry_async(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
) -> Callable[[F], F]:
    """Async version of api_call_with_retry decorator.
    
    Args:
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        backoff_factor: Exponential backoff multiplier.
    
    Returns:
        Decorator function.
    """
    def decorator(func: F) -> F:
        retry_decorated = retry_with_backoff(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff_factor=backoff_factor,
        )(func)
        
        return handle_api_errors_async(log_api_call_async(retry_decorated))  # type: ignore
    
    return decorator


def validate_inputs(**validators):
    """Decorator to validate function inputs.
    
    Args:
        **validators: Keyword arguments mapping parameter names to
                     validator functions.
    
    Returns:
        Decorator function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    validated_value = validator(value)
                    bound.arguments[param_name] = validated_value
            
            return func(*bound.args, **bound.kwargs)
        
        return wrapper  # type: ignore
    
    return decorator
