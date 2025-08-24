"""
Production-ready FastAPI microservice for chat system.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
import time
from datetime import datetime
from typing import Optional

from .config import get_settings
from .models import ChatRequest, ChatResponse, HealthResponse, MetricsResponse
from src.services.chatbot import ChatService
from src.database import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chat Microservice",
    description="Production-ready chat system with persistence",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
chat_service = ChatService()
startup_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await chat_service.initialize()
    logger.info("Chat microservice started successfully")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process chat message with full pipeline"""
    try:
        start_time = time.time()
        
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        response_time = (time.time() - start_time) * 1000
        
        return ChatResponse(
            response=response["response"],
            session_id=response["session_id"],
            response_time_ms=response_time,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(limit: int = 20, offset: int = 0):
    """Return chat history with pagination"""
    try:
        db_manager = get_db_manager()
        history = await db_manager.get_chat_history(limit=limit, offset=offset)
        
        return {
            "items": history,
            "total": len(history),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check database, LLM API, and service health"""
    try:
        # Check database
        db_manager = get_db_manager()
        db_healthy = await db_manager.health_check()
        
        # Check chat service
        service_healthy = await chat_service.health_check()
        
        uptime = time.time() - startup_time
        
        return HealthResponse(
            status="healthy" if db_healthy and service_healthy else "unhealthy",
            database_connected=db_healthy,
            ai_service_connected=service_healthy,
            uptime_seconds=round(uptime, 2),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            ai_service_connected=False,
            uptime_seconds=0,
            timestamp=datetime.now()
        )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Application performance metrics"""
    try:
        db_manager = get_db_manager()
        stats = await db_manager.get_usage_stats()
        
        return MetricsResponse(
            total_requests=stats["total_interactions"],
            average_response_time=stats["average_response_time_ms"],
            uptime_seconds=time.time() - startup_time,
            database_size_mb=stats["database_size_mb"]
        )
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
