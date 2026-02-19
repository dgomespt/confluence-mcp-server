"""Structured logging configuration for Confluence MCP Server.

This module provides structured JSON logging that can be used throughout
the application for consistent log output.
"""
import json
import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add any custom fields from the record
        for key, value in record.__dict__.items():
            if key not in ("msg", "args", "exc_info", "exc_text", "levelname", 
                          "levelno", "pathname", "filename", "module", "lineno",
                          "funcName", "created", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process",
                          "message", "name", "stack_info"):
                if not key.startswith("_"):
                    log_data[key] = value
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development/debugging."""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    structured: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
              Defaults to INFO or LOG_LEVEL env var.
        structured: If True, use JSON structured logging.
        log_file: Optional file path to write logs to.
    
    Returns:
        Configured logger instance.
    """
    # Get log level from env or parameter
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    
    # Create root logger
    logger = logging.getLogger("confluence_mcp")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    if structured:
        # Use JSON formatter for structured logging
        formatter = StructuredFormatter()
    else:
        # Use colored formatter for development
        format_str = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
        formatter = ColoredFormatter(format_str)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ of the module).
    
    Returns:
        Logger instance.
    """
    return logging.getLogger(f"confluence_mcp.{name}")


def log_exception(logger: logging.Logger, message: str, **kwargs):
    """Log an exception with additional context.
    
    Args:
        logger: Logger instance to use.
        message: Error message to log.
        **kwargs: Additional context to include in the log.
    """
    extra = {"extra": kwargs} if kwargs else {}
    logger.exception(message, **extra)


def log_api_call(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """Log an API call with parameters.
    
    Args:
        logger: Logger instance to use.
        method: HTTP method (GET, POST, etc.).
        endpoint: API endpoint being called.
        params: Optional parameters for the call.
        **kwargs: Additional context to include in the log.
    """
    log_data = {
        "api_call": {
            "method": method,
            "endpoint": endpoint,
            "params": params,
        }
    }
    logger.debug(f"API Call: {method} {endpoint}", extra=log_data, **kwargs)


def log_api_response(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    **kwargs
):
    """Log an API response.
    
    Args:
        logger: Logger instance to use.
        method: HTTP method used.
        endpoint: API endpoint called.
        status_code: HTTP status code returned.
        duration_ms: Duration of the call in milliseconds.
        **kwargs: Additional context to include in the log.
    """
    log_data = {
        "api_response": {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }
    }
    logger.info(
        f"API Response: {method} {endpoint} - {status_code} ({duration_ms:.2f}ms)",
        extra=log_data,
        **kwargs
    )
