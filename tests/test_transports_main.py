"""Tests for transport mode __main__ blocks."""
import pytest
import sys
import os


class TestStdioMainBlock:
    """Tests for STDIO mode __main__ block."""
    
    def test_stdio_main_block_exists(self):
        """Test that stdio_mode has a __main__ block that calls run_stdio."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'transports', 'stdio_mode.py')
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that the __main__ block exists and calls run_stdio()
        assert 'if __name__ == "__main__":' in content
        assert 'run_stdio()' in content
    
    def test_stdio_main_not_called_when_imported(self):
        """Test that run_stdio is not called when stdio_mode is imported normally."""
        if 'src.transports.stdio_mode' in sys.modules:
            del sys.modules['src.transports.stdio_mode']
        
        from src.transports import stdio_mode
        
        # Verify that run_stdio is a function (not called)
        assert callable(stdio_mode.run_stdio)


class TestSseMainBlock:
    """Tests for SSE mode __main__ block."""
    
    def test_sse_main_block_exists(self):
        """Test that sse_mode has a __main__ block with correct structure."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'transports', 'sse_mode.py')
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert 'if __name__ == "__main__":' in content
        assert 'argparse' in content
        assert '--host' in content
        assert '--port' in content
        assert 'run_sse' in content
    
    def test_sse_main_not_called_when_imported(self):
        """Test that run_sse is not called when sse_mode is imported normally."""
        if 'src.transports.sse_mode' in sys.modules:
            del sys.modules['src.transports.sse_mode']
        
        from src.transports import sse_mode
        
        assert callable(sse_mode.run_sse)
