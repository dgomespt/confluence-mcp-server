"""Tests for logging_config.py module."""
import os
import pytest
from unittest.mock import patch, MagicMock
from src.core.logging_config import (
    setup_logging,
    get_logger,
)


class TestLoggingConfiguration:
    """Tests for logging configuration."""
    

    
    def test_get_logger(self):
        """Test get_logger function returns logger instance."""
        logger1 = get_logger('test_logger1')
        logger2 = get_logger('test_logger2')
    
        assert logger1 is not None
        assert logger2 is not None
        assert logger1 != logger2
        assert logger1.name == 'confluence_mcp.test_logger1'
        assert logger2.name == 'confluence_mcp.test_logger2'
    
    def test_get_logger_same_name(self):
        """Test get_logger returns the same logger for same name."""
        logger1 = get_logger('test_logger')
        logger2 = get_logger('test_logger')
        
        assert logger1 is logger2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
