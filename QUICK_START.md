# 🚀 Quick Start Guide

Get your AI Financial Marketing Chatbot with **LangChain agent orchestration** running in 5 minutes!

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure API Key
1. Copy `config_template.txt` to `.env`
2. Add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 3: Test Setup
```bash
python test_queries.py
```

## Step 4: Start Backend
```bash
python start_backend.py
```
Backend will be available at: http://localhost:8000

## Step 5: Start Frontend (new terminal)
```bash
python start_frontend.py
```
Frontend will be available at: http://localhost:8501

## 🎉 You're Ready!

Open http://localhost:8501 in your browser and start asking questions about your marketing data!

### Example Questions:
- "What are the top performing campaigns this month?"
- "Show me ROAS by channel"
- "Which segments have the highest funding rates?"

### 🤖 LangChain Agent Features:
- **Smart Tool Selection**: Automatically chooses the right tools for your question
- **Error Recovery**: Retries with different approaches if something fails
- **Conversation Memory**: Remembers context from previous questions
- **Tool Chaining**: Combines multiple tools for complex analysis

### Need Help?
- See the full README.md for detailed documentation
- Check that your OpenAI API key is valid and has credits
- Ensure both backend and frontend are running
- The LangChain agent provides detailed reasoning in verbose mode