#!/usr/bin/env python3
"""Profile Confluence operations for performance analysis."""
import cProfile
import pstats
from io import StringIO

from src.core.confluence_mock import create_mock_confluence
from src.modules.confluence.operations import (
    search_confluence_impl,
    get_page_content_impl,
    list_pages_impl,
)


def profile_operations():
    """Profile the main Confluence operations."""
    mock_confluence = create_mock_confluence()
    
    # Profile search operation
    print("Profiling search_confluence_impl...")
    search_profiler = cProfile.Profile()
    search_profiler.enable()
    for _ in range(100):
        search_confluence_impl(mock_confluence, "onboarding", 5)
    search_profiler.disable()
    search_s = StringIO()
    search_ps = pstats.Stats(search_profiler, stream=search_s).sort_stats("cumulative")
    search_ps.print_stats(10)
    print(search_s.getvalue())
    
    # Profile get page content
    print("\nProfiling get_page_content_impl...")
    get_profiler = cProfile.Profile()
    get_profiler.enable()
    for _ in range(100):
        get_page_content_impl(mock_confluence, "101")
    get_profiler.disable()
    get_s = StringIO()
    get_ps = pstats.Stats(get_profiler, stream=get_s).sort_stats("cumulative")
    get_ps.print_stats(10)
    print(get_s.getvalue())
    
    # Profile list pages
    print("\nProfiling list_pages_impl...")
    list_profiler = cProfile.Profile()
    list_profiler.enable()
    for _ in range(100):
        list_pages_impl(mock_confluence, "ENG", 10)
    list_profiler.disable()
    list_s = StringIO()
    list_ps = pstats.Stats(list_profiler, stream=list_s).sort_stats("cumulative")
    list_ps.print_stats(10)
    print(list_s.getvalue())


if __name__ == "__main__":
    profile_operations()
