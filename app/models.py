"""
Pydantic models for the chat microservice.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    response_time_ms: float
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    ai_service_connected: bool
    uptime_seconds: float
    timestamp: datetime

class MetricsResponse(BaseModel):
    total_requests: int
    average_response_time: float
    uptime_seconds: float
    database_size_mb: float
