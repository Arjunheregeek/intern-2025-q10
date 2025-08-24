"""
Pydantic models for API request/response validation and data security.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ChatHistoryResponse(BaseModel):
    """Response model for chat history entries"""

    id: int
    prompt: str = Field(..., max_length=10000)
    response: str = Field(..., max_length=50000)
    tokens_used: Optional[int] = 0
    timestamp: datetime
    session_id: Optional[str] = None
    response_time_ms: Optional[float] = 0.0

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ChatHistoryListResponse(BaseModel):
    """Response model for paginated chat history"""

    items: List[ChatHistoryResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics"""

    total_interactions: int
    unique_sessions: int
    average_response_time_ms: float
    total_tokens_used: int
    database_size_mb: float


class HealthCheckResponse(BaseModel):
    """Response model for health check"""

    status: str
    timestamp: datetime
    database_connected: bool
    uptime_seconds: float


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    detail: Optional[str] = None
    timestamp: datetime


class ChatRequest(BaseModel):
    """Request model for chat interactions"""

    prompt: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = Field(None, max_length=100)

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()

    @validator("session_id")
    def validate_session_id(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Session ID cannot be empty")
            return v.strip()
        return v
