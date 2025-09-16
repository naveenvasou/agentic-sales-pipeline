from typing import Optional, List, Type, Any
from pydantic import BaseModel, HttpUrl, Field
from langchain.tools.base import BaseTool
import serpapi
import json
import requests
from bs4 import BeautifulSoup
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

serp_api_key = "fd012c64a062d27b1c8a0fbe35833603f570d488e8baeb1c94a7efbb95047d9b"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCnHlsIB-xBfouiUJHcA8dYYg4XMAdNOw0"
genai.configure(api_key="AIzaSyCnHlsIB-xBfouiUJHcA8dYYg4XMAdNOw0")

class Lead(BaseModel):
    """
    Standard structured representation of a lead.
    """
    company_name: str                 # Official name of the company
    domain: Optional[str]             # Company website/domain
    industry: Optional[str]           # Industry/sector
    hq_location: Optional[str]        # Headquarters city/country
    linkedin_url: Optional[HttpUrl]   # LinkedIn profile URL
    source: str                       # Where this lead was found (e.g., "Google Search", "OpenCorporates")

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
    
    def _run(self, query: str, max_results: int = 10) -> str:
        """Execute the search and return results."""
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
                return json.dumps([])
            organic_results = results["organic_results"]
        
            return json.dumps(organic_results)
            
        except Exception as e:
            return f"Error in SerpAPI search: {str(e)}"
    async def _arun(self, query: str, max_results: int = 10):
        """Async version - not implemented for this example."""
        raise NotImplementedError("GoogleSearchTool does not support async execution yet.")
    

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
            for url in urls:
                response = requests.get(url, timeout=10)
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
    
    
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a highly skilled Lead Research Agent. Your primary goal is to find, qualify, and enrich company leads for SaaS products based on a user's Ideal Customer Profile (ICP).

            You have access to the following tools to accomplish your task:

            1.  **GoogleSearchTool**: Use this to search the web for information, especially to find company websites and LinkedIn profiles that match the ICP.
                - **Args**: {{ "query": string, "max_results": int }}
                - **Example**: {{ "query": "top 10 real estate developers in India linkedin.com", "max_results": 10 }}
                - **Returns**: A list of URLs and basic metadata.

            2.  **WebIngestTool**: This tool scrapes content from a list of provided URLs, processes it, and stores it in a vector database for later retrieval.
                - **Args**: {{ "urls": [list of strings] }}
                - **Example**: {{ "urls": ["https://www.example.com", "https://www.another-site.com"] }}
                - **Returns**: A confirmation that the content has been successfully ingested.

            3.  **VectorQueryTool**: Use this to query the information you previously ingested into the vector database. This is your primary method for extracting specific, structured details from company websites.
                - **Args**: {{ "query": string }}
                - **Example**: {{ "query": "Extract the company name, location, number of employees, and primary contact email." }}
                - **Returns**: Structured information about the company.

            ---

            ### Your Workflow

            Follow this exact, multi-step process to fulfill the user's request.
            
             **Step 0: ICP Generation**
            - **Task**: Generate a ICP(Ideal Customer Profile) based of the user input.
            
            **Step 1: Initial Research and List Generation**
            - **Task**: Identify companies that match the user's ICP.
            - **Action**: Use **GoogleSearchTool** with multiple, highly specific queries to find a list of potential company websites and/or LinkedIn profiles. Aim for a diverse list.

            **Step 2: Basic Information Retrieval**
            - **Task**: Scrape and process the web content for each identified company.
            - **Action**: Use **WebIngestTool** on the URLs collected in Step 1. Wait for confirmation that the data is stored in your vector database.

            **Step 3: Initial Data Extraction**
            - **Task**: Get basic details for each company.
            - **Action**: Use **VectorQueryTool** to extract foundational information like company name, location, and industry from the ingested data.

            **Step 4: Iterative Enrichment**
            - **Task**: Deepen your knowledge of each company on the list.
            - **Action**: For each company from your initial list, perform a new cycle of **Search → Ingest → Query** to find and extract more detailed information (e.g., revenue, employee count, specific technology stack, key contact people). Use the `GoogleSearchTool` again with the company's name and specific keywords (e.g., "Company X revenue," "Company X contact").

            **Step 5: Final Output**
            - **Task**: Format all the collected and enriched information.
            - **Action**: Present the final output as a single, valid JSON object. The JSON should be a list of company objects, each containing the structured details you have found.

            ---

            ### Example Final Output
            {{
                "companies": [
                    {{
                        "name": "ABC Builders Pvt Ltd",
                        "location": "Mysore, India",
                        "industry": "Real Estate - Tier 2 Builders",
                        "contact": "info@abcbuilders.com",
                        "size": "200-500 employees",
                        "extra_info": "Known for residential apartments in tier 2 cities"
                    }},
                    {{
                        "name": "XYZ Constructions",
                        "location": "Coimbatore, India",
                        "industry": "Construction",
                        "contact": "contact@xyzconstructions.in",
                        "size": "50-200 employees",
                        "extra_info": "Focus on affordable housing projects"
                    }}
                ]
            }}
            """
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.4 # Use a lower temperature for more predictable tool usage
)

gsearch = GoogleSearchTool(serp_api_key)
webIngest = WebIngestTool()
vectorQuery = VectorQueryTool(webIngest)

tools = [gsearch, webIngest, vectorQuery]

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
response = agent_executor.invoke({
    "input": "I want to sell my saas which is a hotel guest complaint management saas. I am targeting all types of hotels that would want to manage guest comlaints. Maybe have threeshold for number of rooms to guage if a hotel would want my product. location can be popular tourist cities in India. help me find leads"
})

# Print the final answer from the agent
print("\nFinal Answer:")
print(response["output"])