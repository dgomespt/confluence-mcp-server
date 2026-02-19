"""Mock Confluence client for testing."""
import re
from typing import Any, Dict, Optional


class ConfluenceMock:
    """Mock Confluence client that simulates the Atlassian API."""
    
    def __init__(self, url: str = "https://mock.atlassian.net", *args, **kwargs):
        self.url = url
        self._pages: Dict[str, Dict[str, Any]] = {}
        self._search_results: Dict[str, list] = {}
    
    def add_page(self, page_id: str, title: str, content: str, space: str = "TEST"):
        """Add a mock page to the client."""
        self._pages[page_id] = {
            "id": page_id,
            "title": title,
            "body": {"storage": {"value": content}},
            "space": space,
            "_links": {
                "webui": f"/display/{space}/{title.replace(' ', '+')}"
            }
        }
        # Also add to search results for space queries
        space_key = f"space={space} AND type=page"
        if space_key not in self._search_results:
            self._search_results[space_key] = []
        self._search_results[space_key].append({
            "content": {
                "title": title,
                "id": page_id,
                "_links": {"webui": f"/display/{space}/{title.replace(' ', '+')}"}
            }
        })
    
    def add_search_result(self, query: str, results: list):
        """Add mock search results for a query."""
        self._search_results[query] = results
    
    def cql(self, cql_string: str, limit: int = 25) -> Dict[str, Any]:
        """Simulate Confluence CQL search."""
        # Try to match text search: text ~ "query"
        match = re.search(r'text ~ "(.*?)"', cql_string)
        if match:
            query = match.group(1)
            results = self._search_results.get(query, [])
            return {"results": results[:limit]}
        
        # Try to match space query: space=XXX AND type=page
        space_match = re.search(r'space=(\w+)', cql_string)
        if space_match:
            space = space_match.group(1)
            space_key = f"space={space} AND type=page"
            results = self._search_results.get(space_key, [])
            return {"results": results[:limit]}
        
        return {"results": []}
    
    def get_page_by_id(self, page_id: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """Get a page by ID."""
        page = self._pages.get(page_id)
        if page is None:
            raise Exception(f"Page {page_id} not found")
        return page


def create_mock_confluence() -> ConfluenceMock:
    """Create a pre-populated mock Confluence client for testing."""
    mock = ConfluenceMock()
    
    # Add some test pages with spaces
    mock.add_page(
        page_id="101",
        title="Onboarding Guide",
        content="<p>Welcome to the team! This guide will help you get started.</p>",
        space="ENG"
    )
    
    mock.add_page(
        page_id="102", 
        title="API Documentation",
        content="<p>Our API provides endpoints for managing confluence pages.</p>",
        space="DEV"
    )
    
    mock.add_page(
        page_id="103",
        title="Release Notes v1.0",
        content="<p>Version 1.0 includes initial release of the MCP server.</p>",
        space="ENG"
    )
    
    # Add search results for text queries
    mock.add_search_result("onboarding", [
        {
            "content": {
                "title": "Onboarding Guide",
                "id": "101",
                "_links": {"webui": "/display/ENG/Onboarding"}
            }
        }
    ])
    
    mock.add_search_result("api", [
        {
            "content": {
                "title": "API Documentation",
                "id": "102", 
                "_links": {"webui": "/display/DEV/API+Documentation"}
            }
        }
    ])
    
    return mock
