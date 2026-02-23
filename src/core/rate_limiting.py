"""Rate limiting module."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import FastAPI


def add_rate_limiting(app: FastAPI, rate_limit: str = "100/minute") -> Limiter:
    """Add rate limiting to the FastAPI application.
    
    Args:
        app: The FastAPI application to add rate limiting to
        rate_limit: Rate limit string (e.g., "100/minute")
    
    Returns:
        The configured Limiter instance
    """
    limiter = Limiter(key_func=get_remote_address, default_limits=[rate_limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter
