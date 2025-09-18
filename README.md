# Agentic Sales Pipeline 

An intelligent outbound sales automation system built with **LangGraph** and **LangChain**. This multi-agent platform automates lead research, qualification, personalized outreach, and follow-up workflows using AI agents.

##  Project Status

**Currently Implemented:**
- ✅ Lead Research Agent - Fully functional
- ⏳ Lead Qualification Agent - In development
- ⏳ Outreach Agent - In development  
- ⏳ Follow-up Agent - In development
- ⏳ LangGraph Pipeline Integration - Planned

##  Features

### Lead Research Agent (Active)
- **Intelligent Lead Discovery**: Uses Google Search to find companies matching your Ideal Customer Profile (ICP)
- **Web Content Ingestion**: Scrapes and processes company websites for detailed information
- **Vector Database Storage**: Stores scraped content in FAISS for efficient retrieval
- **Smart Information Extraction**: Uses AI to extract structured company data
- **Multi-step Research**: Performs iterative research to enrich lead profiles

##  Prerequisites

- Python 3.8+
- Google API Key (for Gemini)
- SerpAPI Key (for Google Search)

##  Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd agentic-sales-pipeline
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up API keys**
Create a `.env` file in the `tools/` directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

Or set them directly in the code (as shown in current implementation).

##  Usage

### Running the Lead Research Agent

The lead research agent can be used in two ways:

#### 1. Direct Script Execution
```bash
python agents/lead_research.py
```

#### 2. Interactive Chat Interface
```bash
python lead_research_chat.py
```

### Example Usage

```python
# Example prompt for the lead research agent
prompt = """
I want to sell my SaaS which is a hotel guest complaint management system. 
I am targeting all types of hotels that would want to manage guest complaints. 
Maybe have threshold for number of rooms to gauge if a hotel would want my product. 
Location can be popular tourist cities in India. Help me find leads.
"""
```

### Expected Output

The agent will return a structured JSON response:
```json
{
  "companies": [
    {
      "name": "ABC Hotels Pvt Ltd",
      "location": "Goa, India",
      "industry": "Hospitality - Beach Resort",
      "contact": "info@abchotels.com",
      "size": "100+ rooms",
      "extra_info": "Popular beachfront resort chain with multiple properties"
    }
  ]
}
```

##  Project Structure

```
agentic-sales-pipeline/
├── agents/                     # Individual AI agents
│   ├── base_agent.py          # Base agent class
│   ├── lead_research.py       # Lead research agent (active)
│   ├── lead_qualification.py  # Lead qualification (in development)
│   ├── outreach.py           # Outreach agent (in development)
│   └── followup.py           # Follow-up agent (in development)
├── tools/                     # Reusable tools for agents
│   ├── GoogleSearch.py       # Google search functionality
│   ├── WebIngest.py          # Web scraping and vector storage
│   ├── VectorQuery.py        # Vector database querying
│   └── __init__.py           # Tool exports
├── state/                     # Pipeline state management
│   ├── pipeline_state.py     # State schema definition
│   └── __init__.py           
├── lead_research_chat.py      # Interactive chat interface
├── requirements.txt           # Python dependencies
└── README.md                 # Project documentation
```

##  How It Works

### Lead Research Agent Workflow

1. **ICP Generation**: Analyzes user input to create an Ideal Customer Profile
2. **Initial Research**: Uses Google Search to find potential companies
3. **Content Ingestion**: Scrapes company websites and stores in vector database
4. **Data Extraction**: Extracts structured information using AI
5. **Iterative Enrichment**: Performs additional searches for deeper insights
6. **Output Formatting**: Returns structured JSON with company details

### Tools Overview

- **GoogleSearchTool**: Performs web searches using SerpAPI
- **WebIngestTool**: Scrapes websites and creates vector embeddings
- **VectorQueryTool**: Queries the vector database for specific information

## 📝 Configuration

### API Keys Required

1. **Google API Key**: For Gemini language model and embeddings
2. **SerpAPI Key**: For Google search functionality

### Customizable Parameters

- Search location (currently set to India)
- Maximum search results
- Vector database chunk size
- Model temperature settings

## 🤝 Contributing

This project is currently in active development. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Naveen Kumar**

---

**Note**: This project is under active development. The lead research agent is fully functional, while other components are being built progressively. Stay tuned for updates!
