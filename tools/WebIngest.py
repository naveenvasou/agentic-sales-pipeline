from typing import Optional, List, Type, Any
from pydantic import BaseModel, HttpUrl, Field
from langchain.tools.base import BaseTool
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class WebIngestInput(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to scrape and index")

class WebIngestTool(BaseTool):
    name: str = "web_ingest"
    description: str = (
        "Scrapes a list of URLs, cleans the text, chunks it, embeds it, "
        "and stores it into a FAISS vector database for later retrieval. "
        "Input: {urls: list of website URLs}. "
        "Output: A message confirming how many chunks were stored."
    )
    args_schema: Type[BaseModel] = WebIngestInput
    embedding_model:  Any = None
    vectorstore: Any = None

    def __init__(self, embedding_model=None):
        super().__init__()
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = None  # will be initialized after ingestion

    def _run(self, urls: List[str]) -> str:
        try:
            all_texts = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            for url in urls:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove scripts, styles
                for script in soup(["script", "style"]):
                    script.extract()

                text = soup.get_text(separator=" ", strip=True)
                all_texts.append({"source": url, "content": text})

            # Split text into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                length_function=len
            )

            documents = []
            for item in all_texts:
                chunks = splitter.split_text(item["content"])
                for chunk in chunks:
                    documents.append({"page_content": chunk, "metadata": {"source": item["source"]}})

            # Embed and store into FAISS
            self.vectorstore = FAISS.from_texts(
                texts=[d["page_content"] for d in documents],
                embedding=self.embedding_model,
                metadatas=[d["metadata"] for d in documents],
            )

            return f"Successfully ingested {len(documents)} chunks from {len(urls)} URLs into vector store."

        except Exception as e:
            return f"Error during ingestion: {str(e)}"

    async def _arun(self, urls: List[str]) -> str:
        raise NotImplementedError("Async not supported yet.")
    
