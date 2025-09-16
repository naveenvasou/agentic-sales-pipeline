from typing import Optional, List, Type, Any
from pydantic import BaseModel, HttpUrl, Field
from langchain.tools.base import BaseTool
from tools import WebIngestTool
import json
import logging

logger = logging.getLogger(__name__)

class VectorQueryInput(BaseModel):
    query: str = Field(..., description="The natural language query to search for in the vector database")
    top_k: int = Field(5, description="Number of most relevant results to return")


class VectorQueryTool(BaseTool):
    name: str = "vector_query"
    description: str = (
        "Query the FAISS vector database created by WebIngestTool. "
        "Inputs: "
        " - query (string): The question or search phrase. "
        " - top_k (integer, optional, default=5): Number of top results to retrieve. "
        "Output: JSON list of the most relevant text chunks with their source URLs."
    )
    args_schema: Type[BaseModel] = VectorQueryInput
    web_ingest_tool: Any = None
    
    def __init__(self, web_ingest_tool: WebIngestTool):
        super().__init__()
        self.web_ingest_tool = web_ingest_tool
        logger.info("VectorQueryTool initialized.")

    def _run(self, query: str, top_k: int = 5) -> str:
        logger.info(f"Executing vector query: '{query}' with top_k: {top_k}")
        try:
            if self.web_ingest_tool.vectorstore is None:
                logger.warning("Attempted to query an empty vector database. WebIngestTool must be run first.")
                return "Error: No vector database found. Please run WebIngestTool first to ingest documents."

            docs = self.web_ingest_tool.vectorstore.similarity_search(query, k=top_k)
            
            if not docs:
                logger.warning(f"No relevant documents found for query: '{query}'.")
                return f"No relevant information found in the vector database for the query: '{query}'."

            results = [
                {"text": d.page_content, "source": d.metadata.get("source", "unknown")}
                for d in docs
            ]
            
            logger.info(f"Successfully retrieved {len(results)} relevant documents.")
            
            logger.debug(f"Retrieved documents: {json.dumps(results, ensure_ascii=False, indent=2)}")

            return json.dumps(results, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error during vector query for '{query}': {e}", exc_info=True)
            return f"Error during vector query: {str(e)}"

    async def _arun(self, query: str, top_k: int = 5) -> str:
        raise NotImplementedError("Async not supported yet.")