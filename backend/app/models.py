from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatTurn(BaseModel):
    role: str
    content: str

class Filters(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    segment: Optional[str] = None
    channel: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: List[ChatTurn] = Field(default_factory=list)
    filters: Filters = Field(default_factory=Filters)

class TablePayload(BaseModel):
    name: str
    columns: List[str]
    rows: List[List[Any]]

class PlotPayload(BaseModel):
    title: str
    plotly_json: Dict[str, Any]

class ChatResponse(BaseModel):
    answer: str
    actions: List[str]
    sql: Dict[str, Any] | None = None
    tables: List[TablePayload] = Field(default_factory=list)
    plots: List[PlotPayload] = Field(default_factory=list)
    extras: Dict[str, Any] = Field(default_factory=dict)