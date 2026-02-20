"""Tests for async retry functionality in retry.py module."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.core.retry import (
    retry_with_backoff,
    is_retryable_error,
    calculate_delay,
    RETRYABLE_ERROR_CODES,
)
from src.core.exceptions import (
    ConfluenceAPIError,
    ConfluenceRateLimitError,
    ConfluenceAuthenticationError,
    MaxRetriesExceededError,
)


class TestAsyncRetryFunctionality:
    """Tests for async retry decorator."""
    
    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Test async retry decorator with successful function call."""
        mock_func = MagicMock(return_value="success")
        
        @retry_with_backoff(max_retries=2)
        async def test_func():
            return mock_func()
        
        result = await test_func()
        assert result == "success"
        mock_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_retry_retries_on_retryable_error(self):
        """Test async retry decorator retries on retryable errors."""
        mock_func = MagicMock(side_effect=[
            ConfluenceAPIError("Server error", status_code=500),
            ConfluenceAPIError("Server error", status_code=500),
            "success"
        ])
        
        @retry_with_backoff(max_retries=2)
        async def test_func():
            return mock_func()
        
        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_retry_exhausts_retries(self):
        """Test async retry decorator raises MaxRetriesExceededError after exhausting retries."""
        mock_func = MagicMock(side_effect=ConfluenceAPIError("Server error", status_code=500))
        
        @retry_with_backoff(max_retries=2)
        async def test_func():
            return await mock_func()
        
        with pytest.raises(MaxRetriesExceededError):
            await test_func()
        
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_retry_with_retry_after(self):
        """Test async retry decorator with retry_after from rate limit error."""
        mock_func = MagicMock(side_effect=[
            ConfluenceRateLimitError(retry_after=1),
            "success"
        ])
        
        @retry_with_backoff(max_retries=1)
        async def test_func():
            return mock_func()
        
        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_retry_on_non_retryable_error(self):
        """Test async retry decorator raises immediately on non-retryable error."""
        mock_func = MagicMock(side_effect=ConfluenceAuthenticationError())
        
        @retry_with_backoff(max_retries=2)
        async def test_func():
            return await mock_func()
        
        with pytest.raises(ConfluenceAuthenticationError):
            await test_func()
        
        mock_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_retry_with_custom_retryable_errors(self):
        """Test async retry decorator with custom retryable errors list."""
        class CustomRetryableError(Exception):
            pass
        
        mock_func = MagicMock(side_effect=[
            CustomRetryableError(),
            "success"
        ])
        
        @retry_with_backoff(max_retries=1, retryable_errors=(CustomRetryableError,))
        async def test_func():
            return mock_func()
        
        result = await test_func()
        assert result == "success"
        assert mock_func.call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_retry_with_on_retry_callback(self):
        """Test async retry decorator calls on_retry callback."""
        on_retry_callback = MagicMock()
        mock_func = MagicMock(side_effect=[
            ConfluenceAPIError("Server error", status_code=500),
            "success"
        ])
        
        @retry_with_backoff(max_retries=1, on_retry=on_retry_callback)
        async def test_func():
            return mock_func()
        
        result = await test_func()
        assert result == "success"
        on_retry_callback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
