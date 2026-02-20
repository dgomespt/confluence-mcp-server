"""Tests for error_handling.py module."""
import pytest
from unittest.mock import patch, MagicMock
from src.core.error_handling import (
    handle_api_errors,
    log_api_call,
)
from src.core.exceptions import (
    ConfluenceAPIError,
    ConfluenceAuthenticationError,
    ConfluencePermissionError,
    ConfluenceNotFoundError,
    ConfluenceRateLimitError,
    MaxRetriesExceededError,
)


class TestErrorHandlingDecorators:
    """Tests for API error handling decorators."""
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_returns_result(self, mock_get_logger):
        """Test handle_api_errors decorator with successful function call."""
        @handle_api_errors
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_raises_not_found(self, mock_get_logger):
        """Test handle_api_errors decorator with 404 error."""
        @handle_api_errors
        def test_func():
            raise ConfluenceNotFoundError("Page", "123")
    
        # Should not raise an exception (decorator catches it)
        result = test_func()
        assert isinstance(result, str)
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_raises_authentication_error(self, mock_get_logger):
        """Test handle_api_errors decorator with authentication error."""
        @handle_api_errors
        def test_func():
            raise ConfluenceAuthenticationError()
    
        result = test_func()
        assert isinstance(result, str)
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_raises_permission_error(self, mock_get_logger):
        """Test handle_api_errors decorator with permission error."""
        @handle_api_errors
        def test_func():
            raise ConfluencePermissionError()
    
        result = test_func()
        assert isinstance(result, str)
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_raises_rate_limit_error(self, mock_get_logger):
        """Test handle_api_errors decorator with rate limit error."""
        @handle_api_errors
        def test_func():
            raise ConfluenceRateLimitError(retry_after=60)
    
        result = test_func()
        assert isinstance(result, str)
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_raises_max_retries(self, mock_get_logger):
        """Test handle_api_errors decorator with max retries error."""
        @handle_api_errors
        def test_func():
            raise MaxRetriesExceededError("Max retries exceeded")
    
        result = test_func()
        assert isinstance(result, str)
    
    @patch('src.core.error_handling.get_logger')
    def test_handle_api_errors_handles_generic_exception(self, mock_get_logger):
        """Test handle_api_errors decorator with generic exception."""
        @handle_api_errors
        def test_func():
            raise Exception("Generic error")
    
        result = test_func()
        assert isinstance(result, str)
    



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
