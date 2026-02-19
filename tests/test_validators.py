"""Tests for validators and error handling."""
import pytest
from unittest.mock import MagicMock, patch

from src.core.validators import (
    validate_query,
    validate_page_id,
    validate_space_key,
    validate_limit,
    validate_boolean,
    sanitize_string,
    validate_and_sanitize_search_params,
    validate_and_sanitize_page_params,
    validate_and_sanitize_list_params,
)
from src.core.exceptions import (
    InvalidQueryError,
    InvalidPageIdError,
    InvalidSpaceKeyError,
    InvalidLimitError,
    ValidationError,
)
from src.core.retry import (
    is_retryable_error,
    calculate_delay,
    retry_with_backoff,
)
from src.core.exceptions import (
    ConfluenceAPIError,
    ConfluenceNotFoundError,
    ConfluenceRateLimitError,
    ConfluenceAuthenticationError,
    MaxRetriesExceededError,
)


class TestValidateQuery:
    """Tests for query validation."""
    
    def test_valid_query(self):
        """Test that a valid query passes validation."""
        result = validate_query("test query")
        assert result == "test query"
    
    def test_query_strips_whitespace(self):
        """Test that query whitespace is stripped."""
        result = validate_query("  test query  ")
        assert result == "test query"
    
    def test_empty_query_raises_error(self):
        """Test that empty query raises error."""
        with pytest.raises(InvalidQueryError):
            validate_query("")
    
    def test_none_query_raises_error(self):
        """Test that None query raises error."""
        with pytest.raises(InvalidQueryError):
            validate_query(None)
    
    def test_whitespace_only_query_raises_error(self):
        """Test that whitespace-only query raises error."""
        with pytest.raises(InvalidQueryError):
            validate_query("   ")
    
    def test_query_too_long_raises_error(self):
        """Test that query exceeding max length raises error."""
        long_query = "a" * 501
        with pytest.raises(InvalidQueryError):
            validate_query(long_query)


class TestValidatePageId:
    """Tests for page ID validation."""
    
    def test_valid_page_id(self):
        """Test that a valid page ID passes validation."""
        result = validate_page_id("12345")
        assert result == "12345"
    
    def test_page_id_with_hyphen(self):
        """Test that page ID with hyphen is valid."""
        result = validate_page_id("123-456")
        assert result == "123-456"
    
    def test_page_id_with_underscore(self):
        """Test that page ID with underscore is valid."""
        result = validate_page_id("123_456")
        assert result == "123_456"
    
    def test_empty_page_id_raises_error(self):
        """Test that empty page ID raises error."""
        with pytest.raises(InvalidPageIdError):
            validate_page_id("")
    
    def test_invalid_page_id_raises_error(self):
        """Test that invalid page ID raises error."""
        with pytest.raises(InvalidPageIdError):
            validate_page_id("page@123")
    
    def test_page_id_strips_whitespace(self):
        """Test that page ID whitespace is stripped."""
        result = validate_page_id("  12345  ")
        assert result == "12345"


class TestValidateSpaceKey:
    """Tests for space key validation."""
    
    def test_valid_space_key(self):
        """Test that a valid space key passes validation."""
        result = validate_space_key("ENG")
        assert result == "ENG"
    
    def test_space_key_uppercase(self):
        """Test that space key is converted to uppercase."""
        result = validate_space_key("eng")
        assert result == "ENG"
    
    def test_space_key_with_hyphen(self):
        """Test that space key with hyphen is valid."""
        result = validate_space_key("ENG-Dev")
        assert result == "ENG-DEV"
    
    def test_empty_space_key_raises_error(self):
        """Test that empty space key raises error."""
        with pytest.raises(InvalidSpaceKeyError):
            validate_space_key("")
    
    def test_space_key_too_long_raises_error(self):
        """Test that space key exceeding max length raises error."""
        with pytest.raises(InvalidSpaceKeyError):
            validate_space_key("TOOLONGSPACEKEY")
    
    def test_invalid_space_key_raises_error(self):
        """Test that invalid space key raises error."""
        # Underscore is not valid in Confluence space keys
        with pytest.raises(InvalidSpaceKeyError):
            validate_space_key("ENG_D")


class TestValidateLimit:
    """Tests for limit validation."""
    
    def test_valid_limit(self):
        """Test that a valid limit passes validation."""
        result = validate_limit(10)
        assert result == 10
    
    def test_default_limit(self):
        """Test that limit is within valid range."""
        result = validate_limit(1)
        assert result == 1
    
    def test_max_limit(self):
        """Test that max limit passes validation."""
        result = validate_limit(100)
        assert result == 100
    
    def test_limit_below_min_raises_error(self):
        """Test that limit below minimum raises error."""
        with pytest.raises(InvalidLimitError):
            validate_limit(0)
    
    def test_limit_above_max_raises_error(self):
        """Test that limit above maximum raises error."""
        with pytest.raises(InvalidLimitError):
            validate_limit(101)
    
    def test_limit_from_string(self):
        """Test that limit can be converted from string."""
        result = validate_limit("10")
        assert result == 10
    
    def test_invalid_limit_type_raises_error(self):
        """Test that invalid limit type raises error."""
        with pytest.raises(InvalidLimitError):
            validate_limit("invalid")


class TestValidateBoolean:
    """Tests for boolean validation."""
    
    def test_valid_boolean(self):
        """Test that boolean passes validation."""
        assert validate_boolean(True) is True
        assert validate_boolean(False) is False
    
    def test_string_true_values(self):
        """Test that string true values convert correctly."""
        assert validate_boolean("true") is True
        assert validate_boolean("1") is True
        assert validate_boolean("yes") is True
        assert validate_boolean("on") is True
    
    def test_string_false_values(self):
        """Test that string false values convert correctly."""
        assert validate_boolean("false") is False
        assert validate_boolean("0") is False
        assert validate_boolean("no") is False
        assert validate_boolean("off") is False
    
    def test_none_returns_default(self):
        """Test that None returns default value."""
        assert validate_boolean(None, default=True) is True
        assert validate_boolean(None, default=False) is False
    
    def test_invalid_raises_error(self):
        """Test that invalid value raises error."""
        with pytest.raises(ValidationError):
            validate_boolean("invalid")


class TestRetryLogic:
    """Tests for retry logic."""
    
    def test_is_retryable_error_rate_limit(self):
        """Test that rate limit errors are retryable."""
        error = ConfluenceRateLimitError(retry_after=60)
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_auth(self):
        """Test that authentication errors are not retryable."""
        error = ConfluenceAuthenticationError()
        assert is_retryable_error(error) is False
    
    def test_is_retryable_error_server_error(self):
        """Test that server errors are retryable."""
        error = ConfluenceAPIError("Server error", status_code=500)
        assert is_retryable_error(error) is True
    
    def test_calculate_delay_exponential(self):
        """Test that delay increases exponentially."""
        delay_0 = calculate_delay(0, initial_delay=1.0, backoff_factor=2.0)
        delay_1 = calculate_delay(1, initial_delay=1.0, backoff_factor=2.0)
        delay_2 = calculate_delay(2, initial_delay=1.0, backoff_factor=2.0)
        
        # Each delay should be roughly double the previous
        assert delay_1 > delay_0
        assert delay_2 > delay_1
    
    def test_calculate_delay_max_delay(self):
        """Test that delay doesn't exceed max."""
        delay = calculate_delay(10, initial_delay=1.0, max_delay=5.0, backoff_factor=2.0)
        assert delay <= 5.0
    
    def test_retry_success(self):
        """Test that function succeeds after retry."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary error")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 2
    
    def test_retry_exhausted(self):
        """Test that error is raised after max retries."""
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def test_func():
            raise Exception("Persistent error")
        
        with pytest.raises(MaxRetriesExceededError):
            test_func()


class TestSanitizeString:
    """Tests for string sanitization."""
    
    def test_sanitize_basic(self):
        """Test basic string sanitization."""
        result = sanitize_string("  test  ")
        assert result == "test"
    
    def test_sanitize_max_length(self):
        """Test string truncation."""
        result = sanitize_string("a" * 100, max_length=10)
        assert len(result) == 10
    
    def test_sanitize_strip_html(self):
        """Test HTML stripping."""
        result = sanitize_string("<p>test</p>", strip_html=True)
        assert result == "test"
    
    def test_sanitize_none_returns_empty(self):
        """Test that None returns empty string."""
        result = sanitize_string(None)
        assert result == ""


class TestValidationCombinations:
    """Tests for combined validation functions."""
    
    def test_search_params_validation(self):
        """Test search params validation."""
        query, limit = validate_and_sanitize_search_params("test", 10)
        assert query == "test"
        assert limit == 10
    
    def test_page_params_validation(self):
        """Test page params validation."""
        page_id, convert = validate_and_sanitize_page_params("123", True)
        assert page_id == "123"
        assert convert is True
    
    def test_list_params_validation(self):
        """Test list params validation."""
        space, limit = validate_and_sanitize_list_params("ENG", 10)
        assert space == "ENG"
        assert limit == 10
