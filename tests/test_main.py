"""Tests for main.py entry point."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.main import main


class TestMainEntryPoint:
    """Tests for the main entry point function."""
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_default_transport(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with default transport (stdio)."""
        mock_getenv.side_effect = lambda key, default=None: default
        
        with patch('src.transports.stdio_mode.run_stdio') as mock_run_stdio:
            main()
            
            mock_setup_logging.assert_called_once()
            mock_run_stdio.assert_called_once()
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_sse_transport(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with SSE transport."""
        mock_getenv.side_effect = lambda key, default=None: 'sse' if key == 'MCP_TRANSPORT' else default
        
        with patch('src.transports.sse_mode.run_sse') as mock_run_sse:
            with patch('src.main.Config.from_env_optional') as mock_from_env_optional:
                mock_config = MagicMock()
                mock_config.host = '127.0.0.1'
                mock_config.port = 8080
                mock_from_env_optional.return_value = mock_config
                
                main()
                
                mock_run_sse.assert_called_once_with(host='127.0.0.1', port=8080)
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_sse_no_config(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with SSE transport and no config."""
        mock_getenv.side_effect = lambda key, default=None: 'sse' if key == 'MCP_TRANSPORT' else default
        
        with patch('src.transports.sse_mode.run_sse') as mock_run_sse:
            with patch('src.main.Config.from_env_optional') as mock_from_env_optional:
                mock_from_env_optional.return_value = None
                
                main()
                
                mock_run_sse.assert_called_once_with(host='127.0.0.1', port=8080)
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_with_custom_log_level(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with custom log level."""
        mock_getenv.side_effect = lambda key, default=None: 'DEBUG' if key == 'LOG_LEVEL' else default
        
        with patch('src.transports.stdio_mode.run_stdio') as mock_run_stdio:
            main()
            
            mock_setup_logging.assert_called_once_with(level='DEBUG', structured=False)
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_with_structured_logging(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with structured logging."""
        mock_getenv.side_effect = lambda key, default=None: 'true' if key == 'LOG_STRUCTURED' else default
        
        with patch('src.transports.stdio_mode.run_stdio') as mock_run_stdio:
            main()
            
            mock_setup_logging.assert_called_once_with(level='INFO', structured=True)
    
    @patch('src.main.os.getenv')
    @patch('src.main.setup_logging')
    @patch('src.main.get_logger')
    def test_main_with_structured_logging_false(self, mock_get_logger, mock_setup_logging, mock_getenv):
        """Test main function with structured logging disabled."""
        mock_getenv.side_effect = lambda key, default=None: 'false' if key == 'LOG_STRUCTURED' else default
        
        with patch('src.transports.stdio_mode.run_stdio') as mock_run_stdio:
            main()
            
            mock_setup_logging.assert_called_once_with(level='INFO', structured=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
