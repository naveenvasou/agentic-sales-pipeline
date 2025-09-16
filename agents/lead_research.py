import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools import GoogleSearchTool, WebIngestTool, VectorQueryTool
from langchain.memory import ConversationSummaryBufferMemory
import logging

logging.basicConfig(filename='agent_run.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
global serp_api_key 

def setup_api_keys():
    global serp_api_key 
    serp_api_key = "fd012c64a062d27b1c8a0fbe35833603f570d488e8baeb1c94a7efbb95047d9b"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCnHlsIB-xBfouiUJHcA8dYYg4XMAdNOw0"
    logging.info("API keys set up successfully.")

def create_lead_generation_agent():
    """
    Creates and returns a configured LangChain agent executor for lead generation.
    """
    setup_api_keys()
    logging.info("Starting the Lead Generation Agent creation process.")

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
    logging.info("ChatPromptTemplate initialized.")
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.4 
    )
    logging.info("LLM model configured.")
    
    try:
        gsearch = GoogleSearchTool(serp_api_key)
        webIngest = WebIngestTool()
        vectorQuery = VectorQueryTool(webIngest)
        tools = [gsearch, webIngest, vectorQuery]
        logging.info("Tools successfully initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize tools: {e}")
        return f"Failed to initialize tools: {e}"

    tools = [gsearch, webIngest, vectorQuery]
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=2000, memory_key="chat_history")
    logging.info("ConversationSummaryBufferMemory configured.")
    agent = create_tool_calling_agent(llm, tools, prompt)
    logging.info("Agent created using create_tool_calling_agent.")
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    logging.info("AgentExecutor initialized.")
    return agent_executor