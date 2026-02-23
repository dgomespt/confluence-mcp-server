"""Tests for the transport modes (STDIO and SSE)."""
import pytest
import os
from unittest.mock import MagicMock, patch

from src.transports.stdio_mode import run_stdio
from src.transports.sse_mode import run_sse


class TestStdioMode:
    """Tests for STDIO transport mode."""
    
    @patch('src.transports.stdio_mode.create_mcp_app')
    @patch('src.transports.stdio_mode.setup_logging')
    @patch('src.transports.stdio_mode.logger')
    def test_run_stdio_creates_app_without_metrics(self, mock_logger, mock_setup_logging, mock_create_app):
        """Test that run_stdio creates an app with include_metrics=False."""
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        # Run with timeout to prevent blocking
        import threading
        import time
        
        def run():
            try:
                run_stdio()
            except Exception:
                pass
        
        thread = threading.Thread(target=run)
        thread.start()
        time.sleep(0.1)
        
        # Verify create_app was called with include_metrics=False
        mock_create_app.assert_called_once_with(include_metrics=False)
        
        # Verify app.run was called
        mock_app.run.assert_called_once()
    
    @patch('src.transports.stdio_mode.create_mcp_app')
    @patch('src.transports.stdio_mode.setup_logging')
    @patch('src.transports.stdio_mode.logger')
    def test_run_stdio_with_structured_logging(self, mock_logger, mock_setup_logging, mock_create_app):
        """Test run_stdio with structured logging enabled."""
        os.environ['LOG_STRUCTURED'] = 'true'
        
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        try:
            import threading
            import time
            
            def run():
                try:
                    run_stdio()
                except Exception:
                    pass
            
            thread = threading.Thread(target=run)
            thread.start()
            time.sleep(0.1)
            
            mock_setup_logging.assert_called_once_with(structured=True)
        finally:
            del os.environ['LOG_STRUCTURED']
    
    @patch('src.transports.stdio_mode.create_mcp_app')
    @patch('src.transports.stdio_mode.setup_logging')
    @patch('src.transports.stdio_mode.logger')
    def test_run_stdio_without_structured_logging(self, mock_logger, mock_setup_logging, mock_create_app):
        """Test run_stdio with structured logging disabled."""
        os.environ['LOG_STRUCTURED'] = 'false'
        
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        try:
            import threading
            import time
            
            def run():
                try:
                    run_stdio()
                except Exception:
                    pass
            
            thread = threading.Thread(target=run)
            thread.start()
            time.sleep(0.1)
            
            mock_setup_logging.assert_called_once_with(structured=False)
        finally:
            del os.environ['LOG_STRUCTURED']


class TestSseMode:
    """Tests for SSE transport mode."""
    
    @patch('src.transports.sse_mode.uvicorn.run')
    @patch('src.transports.sse_mode.create_mcp_app')
    @patch('src.transports.sse_mode.setup_logging')
    @patch('src.transports.sse_mode.logger')
    def test_run_sse_creates_app_with_metrics(self, mock_logger, mock_setup_logging, mock_create_app, mock_uvicorn_run):
        """Test that run_sse creates an app with include_metrics=True."""
        mock_app = MagicMock()
        mock_app.sse_app.return_value = MagicMock()
        mock_create_app.return_value = mock_app
        
        run_sse(host='127.0.0.1', port=8080)
        
        mock_create_app.assert_called_once_with(include_metrics=True)
        mock_uvicorn_run.assert_called_once()
    
    @patch('src.transports.sse_mode.uvicorn.run')
    @patch('src.transports.sse_mode.create_mcp_app')
    @patch('src.transports.sse_mode.setup_logging')
    @patch('src.transports.sse_mode.logger')
    def test_run_sse_with_custom_host_port(self, mock_logger, mock_setup_logging, mock_create_app, mock_uvicorn_run):
        """Test run_sse with custom host and port."""
        mock_app = MagicMock()
        mock_app.sse_app.return_value = MagicMock()
        mock_create_app.return_value = mock_app
        
        run_sse(host='0.0.0.0', port=9090)
        
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        
        assert call_args[1]['host'] == '0.0.0.0'
        assert call_args[1]['port'] == 9090
    
    @patch('src.transports.sse_mode.uvicorn.run')
    @patch('src.transports.sse_mode.create_mcp_app')
    @patch('src.transports.sse_mode.setup_logging')
    @patch('src.transports.sse_mode.logger')
    def test_run_sse_with_structured_logging(self, mock_logger, mock_setup_logging, mock_create_app, mock_uvicorn_run):
        """Test run_sse with structured logging enabled."""
        os.environ['LOG_STRUCTURED'] = 'true'
        
        mock_app = MagicMock()
        mock_app.sse_app.return_value = MagicMock()
        mock_create_app.return_value = mock_app
        
        try:
            run_sse()
            mock_setup_logging.assert_called_once_with(structured=True)
        finally:
            del os.environ['LOG_STRUCTURED']
    
    @patch('src.transports.sse_mode.uvicorn.run')
    @patch('src.transports.sse_mode.create_mcp_app')
    @patch('src.transports.sse_mode.setup_logging')
    @patch('src.transports.sse_mode.logger')
    def test_run_sse_without_structured_logging(self, mock_logger, mock_setup_logging, mock_create_app, mock_uvicorn_run):
        """Test run_sse with structured logging disabled."""
        os.environ['LOG_STRUCTURED'] = 'false'
        
        mock_app = MagicMock()
        mock_app.sse_app.return_value = MagicMock()
        mock_create_app.return_value = mock_app
        
        try:
            run_sse()
            mock_setup_logging.assert_called_once_with(structured=False)
        finally:
            del os.environ['LOG_STRUCTURED']
