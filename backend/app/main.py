import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from .models import ChatRequest, ChatResponse
from .config import settings
from .agents import process_chat_request

app = FastAPI(default_response_class=ORJSONResponse, title="AI Financial Marketing Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        filters = req.filters.model_dump()
        history = [t.model_dump() for t in req.history]
        result = process_chat_request(req.message, filters, history)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kpi")
async def get_kpis(filters: dict):
    """Get KPI summary data directly without LLM"""
    try:
        from .tools import query_marketing_data
        result = query_marketing_data.invoke({
            'template': 'KPI_SUMMARY',
            'date_from': filters.get('date_from', '2025-08-01'),
            'date_to': filters.get('date_to', '2025-09-18'),
            'segment': filters.get('segment'),
            'channel': filters.get('channel')
        })
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/channel-performance")
async def get_channel_performance(filters: dict):
    """Get channel performance data directly without LLM"""
    try:
        from .tools import query_marketing_data
        result = query_marketing_data.invoke({
            'template': 'CHANNEL_PERFORMANCE',
            'date_from': filters.get('date_from', '2025-08-01'),
            'date_to': filters.get('date_to', '2025-09-18'),
            'segment': filters.get('segment'),
            'channel': filters.get('channel')
        })
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))