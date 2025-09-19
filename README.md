# AI Financial Marketing Chatbot

An AI-powered analytics chatbot for financial services marketing data, built with FastAPI backend, Streamlit frontend, and **LangChain agent orchestration**. The system provides natural language querying of marketing performance data, loan metrics, and customer analytics using intelligent tool-calling agents.

## Features

- 🤖 **LangChain Agent Framework**: Intelligent tool orchestration and reasoning
- 💬 **Natural Language Queries**: Ask questions in plain English about marketing performance
- 📊 **Interactive Dashboard**: KPI cards, trends, and channel performance metrics
- 📈 **Dynamic Visualizations**: Auto-generated charts based on your queries
- 🔒 **Secure SQL**: Allowlisted, parameterized queries prevent SQL injection
- 🎯 **Financial Services Focus**: Optimized for loan marketing, funding rates, and ROAS analysis
- 🛠️ **Tool-Based Architecture**: Modular tools for data querying, visualization, and analysis

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment

#### Option A: Guided Setup (Recommended)
```bash
python setup_env.py
```
This interactive script will help you choose between OpenAI and Azure OpenAI and create the `.env` file with the correct `LLM_PROVIDER` setting.

#### Option B: Manual Setup
Copy the configuration template and add your API keys:

```bash
cp config_template.txt .env
# Then edit .env with your actual values
```

Your `.env` file should contain:
```env
# REQUIRED: Choose your LLM provider first!
LLM_PROVIDER=openai  # or "azure" for Azure OpenAI

# For OpenAI API (when LLM_PROVIDER=openai)
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini

# For Azure OpenAI (when LLM_PROVIDER=azure)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

DATABASE_URL=sqlite:///marketing.db
ALLOWED_ORIGINS=*
API_BASE=http://localhost:8000
```

#### Test Your Configuration
```bash
python test_llm_init.py
```

#### Azure OpenAI Configuration

If you prefer to use Azure OpenAI instead of the standard OpenAI API:

1. **Set LLM Provider to Azure:**
   ```
   LLM_PROVIDER=azure
   ```

2. **Configure Azure OpenAI Settings:**
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
   - `AZURE_OPENAI_DEPLOYMENT`: Your model deployment name
   - `AZURE_OPENAI_API_VERSION`: The API version (recommended: 2024-02-15-preview)

3. **Example Azure Configuration:**
   ```
   LLM_PROVIDER=azure
   AZURE_OPENAI_API_KEY=abcd1234567890abcd1234567890abcd
   AZURE_OPENAI_ENDPOINT=https://my-openai-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

### 3. Run the Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 4. Run the Frontend (in another terminal)

```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

### 5. Open Your Browser

Navigate to `http://localhost:8501` to access the chatbot interface.

## Data Schema

The system works with a financial services marketing dataset containing:

- **Customer Data**: Applications, demographics, risk profiles
- **Marketing Attribution**: Channels, campaigns, costs, touchpoints  
- **Loan Performance**: Funding rates, amounts, approval rates
- **Revenue Metrics**: Daily revenue, LTV, servicing costs

## Example Queries

Try asking these questions in the chatbot:

- "What are the top performing campaigns this month?"
- "Show me ROAS by channel for the last 30 days"
- "Which customer segments have the highest funding rates?"
- "Trend of applications and revenue over time"
- "What's the cost per funded loan by channel?"

## Available Analysis Types

- **KPI Summary**: Overall performance metrics and trends
- **Campaign Performance**: Top/bottom performers by ROAS, volume
- **Channel Analysis**: Attribution, cost efficiency, conversion rates
- **Segment Analysis**: Customer demographics and behavior

## Architecture

```
[Streamlit Frontend] 
       ↓ HTTP
[FastAPI Backend]
       ↓
[LangChain Agent Executor]
  ├── 🛠️ query_marketing_data (SQL tool)
  ├── 📊 create_visualization (Plotly tool)  
  ├── 🧠 analyze_data_insights (Analysis tool)
  └── 🤖 OpenAI GPT (orchestration & reasoning)
       ↓
[SQLite Database]
```

### LangChain Benefits:
- **Intelligent Tool Selection**: Agent automatically chooses the right tools based on user queries
- **Error Handling**: Built-in retry logic and error recovery
- **Memory Management**: Conversation context maintained across interactions
- **Extensibility**: Easy to add new tools and capabilities

## Security Features

- ✅ Read-only database access
- ✅ Allowlisted SQL templates only
- ✅ Parameterized queries prevent injection
- ✅ No sensitive data in logs
- ✅ Environment-based configuration

## API Endpoints

- `POST /chat` - Main chatbot endpoint
- `GET /health` - Health check
- Backend runs on port 8000 by default

## 🛠️ Troubleshooting

### Quick Fixes

**Streamlit Width/Layout Issues:**
```bash
# Ensure compatible Streamlit version
pip install streamlit>=1.28.0,<1.39.0
```

**Azure OpenAI Proxy/Connection Errors:**
```bash
# Run the Azure troubleshooting script
python fix_azure_issues.py
```

**LLM Configuration Issues:**
```bash
# Test your LLM setup
python test_llm_init.py
```

### Common Issues

**1. Streamlit Layout Problems**
- Clear browser cache and restart Streamlit
- The app uses `use_container_width=True` for compatibility
- Page is automatically configured for wide layout

**2. Azure OpenAI Issues**
- **Proxy Errors**: Run `python fix_azure_issues.py` to automatically fix
- **Authentication**: Verify credentials match your Azure portal exactly
- **Network**: App automatically bypasses proxies for Azure domains

**3. Backend Issues**
- Ensure your OpenAI/Azure API key is valid and has credits
- Check that the database file exists and is readable
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Make sure backend is running on port 8001 (not 8000)

**4. Frontend Issues**  
- Check that API_BASE in your .env matches the backend URL (port 8001)
- Verify Streamlit dependencies are installed
- Clear browser cache if layout issues persist

**5. Database Issues**
- The database should be in the root directory as `marketing.db`
- Ensure the database is not locked by other processes

### Azure OpenAI Specific Troubleshooting

**Proxy Errors (even without proxies):**
1. Run `python fix_azure_issues.py` - automatically fixes proxy issues
2. Manually clear if needed: `unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy`

**Authentication Errors:**
1. Verify Azure OpenAI credentials in Azure portal
2. Ensure deployment name matches exactly (case-sensitive)
3. Check endpoint format: `https://your-resource.openai.azure.com/`

**Connection Test:**
```bash
python fix_azure_issues.py  # Comprehensive Azure testing
python test_llm_init.py     # General LLM configuration test
```

## Development

### Project Structure
```
├── backend/
│   └── app/
│       ├── main.py          # FastAPI app
│       ├── agents.py        # LangChain agent orchestration
│       ├── tools.py         # LangChain tools (NEW)
│       ├── sql.py           # Database queries
│       ├── models.py        # Pydantic models
│       └── config.py        # Settings
├── frontend/
│   ├── streamlit_app.py     # Main UI
│   └── styles.css           # Custom styling
├── marketing.db             # SQLite database
├── requirements.txt         # Dependencies (includes LangChain)
└── README.md               # This file
```

### Adding New Tools/Capabilities

1. **New SQL Template**: Add to `ALLOWED_QUERIES` in `backend/app/sql.py`
2. **New LangChain Tool**: Create in `backend/app/tools.py` using `@tool` decorator
3. **Register Tool**: Add to `MARKETING_TOOLS` list in `tools.py`
4. **Test**: The LangChain agent will automatically discover and use new tools

### LangChain Agent Advantages

- **Dynamic Tool Selection**: Agent chooses optimal tools based on context
- **Error Recovery**: Automatic retry with different approaches
- **Conversation Memory**: Maintains context across multiple exchanges
- **Tool Composition**: Can chain multiple tools for complex queries

## Production Deployment

For production deployment:

1. Use environment variables for all secrets
2. Deploy behind a reverse proxy (nginx/traefik)
3. Use a production WSGI server (gunicorn)
4. Consider using PostgreSQL instead of SQLite
5. Add authentication/authorization as needed
6. Set up monitoring and logging

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the example queries and data schema
- Ensure your OpenAI API key has sufficient credits