from typing import Optional, List, Type, Any
from pydantic import BaseModel, HttpUrl, Field
from langchain.tools.base import BaseTool
import serpapi
import json
import logging

logger = logging.getLogger(__name__)

class GoogleSearchInput(BaseModel):
    query: str = Field(..., description="The search query string")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class GoogleSearchTool(BaseTool):
    """Tool for searching companies using SerpAPI Google Search."""
    
    name: str = "google_search"
    description: str = (
        "Use this tool to perform a Google search via SerpAPI. "
        "Args: "
        " - query (string): The exact search phrase to look up on Google. "
        " - max_results (integer, optional, default=10): The maximum number of results to return. "
        "Outputs: A JSON string containing a list of search results. "
        "Each result object may include the following keys: "
        " - 'position' (int): position of the result in the search page"
        " - 'title' (string): The title of the search result. "
        " - 'link' (string): The direct URL to the result. "
        " - 'snippet' (string): A short description or preview text of the result. "
        "Example Input: {\"query\": \"hotel Goa \\\"poor reviews\\\" OR \\\"guest complaints\\\" site:tripadvisor.com\", \"max_results\": 15} "
        "Example Output: "
        "[{\"title\": \"ABC Events\", \"link\": \"https://abcevents.com\", \"snippet\": \"Leading event management company in Bangalore...\"}, ...]"
    )
    args_schema: Type[BaseModel] = GoogleSearchInput
    api_key: str = ""
    base_url: str = ""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        logger.info("GoogleSearchTool initialized.")
    
    def _run(self, query: str, max_results: int = 10) -> str:
        """Execute the search and return results."""
        logger.info(f"Executing Google search with query: '{query}' and max_results: {max_results}")
        try:
            params = {
                "engine": "google_light",
                "q": query,
                "location": "Bangalore, India",
                "google_domain": "google.com",
                "hl": "en",
                "gl": "in",
                "api_key": self.api_key,
                "num" : max_results
            }
            
            results = serpapi.search(params)
            
            if "organic_results" not in results:
                logger.warning(f"No organic results found for query: '{query}'.")
                return json.dumps([])
            
            organic_results = results["organic_results"]
            logger.info(f"Successfully retrieved {len(organic_results)} organic results.")
            
            logger.debug(f"Full search results: {json.dumps(organic_results, indent=2)}")
            
            return json.dumps(organic_results)
            
        except Exception as e:
            logger.error(f"Error in SerpAPI search for query '{query}': {e}", exc_info=True)
            return f"Error in SerpAPI search: {str(e)}"
    
    async def _arun(self, query: str, max_results: int = 10):
        """Async version - not implemented for this example."""
        raise NotImplementedError("GoogleSearchTool does not support async execution yet.")