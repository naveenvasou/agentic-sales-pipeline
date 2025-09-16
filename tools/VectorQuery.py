from typing import Optional, List, Type, Any
from pydantic import BaseModel, HttpUrl, Field
from langchain.tools.base import BaseTool

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

    def _run(self, query: str, top_k: int = 5) -> str:
        try:
            if self.web_ingest_tool.vectorstore is None:
                return "Error: No vector database found. Please run WebIngestTool first to ingest documents."

            docs = self.web_ingest_tool.vectorstore.similarity_search(query, k=top_k)
            results = [
                {"text": d.page_content, "source": d.metadata.get("source", "unknown")}
                for d in docs
            ]
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)

        except Exception as e:
            return f"Error during vector query: {str(e)}"

    async def _arun(self, query: str, top_k: int = 5) -> str:
        raise NotImplementedError("Async not supported yet.")