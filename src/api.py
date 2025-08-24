"""
FastAPI application with endpoints, security, and comprehensive logging.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from datetime import datetime
from typing import Optional

try:
    from models import (
        ChatHistoryResponse, ChatHistoryListResponse, 
        UsageStatsResponse, HealthCheckResponse
    )
    from database import db_manager
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure models.py and database.py exist in the src directory")
    raise

# Configure logging
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Chat Persistence API",
    description="REST API for chat history management with persistence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

startup_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await db_manager.initialize()
        logger.info("API server started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        await db_manager.get_usage_stats()
        db_connected = True
    except Exception:
        db_connected = False
    
    uptime = time.time() - startup_time
    
    return HealthCheckResponse(
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.now(),
        database_connected=db_connected,
        uptime_seconds=round(uptime, 2)
    )

@app.get("/history", response_model=ChatHistoryListResponse)
async def get_chat_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get paginated chat history"""
    try:
        history = await db_manager.get_chat_history(limit, offset)
        total = len(history)
        
        return ChatHistoryListResponse(
            items=[ChatHistoryResponse(**item) for item in history],
            total=total,
            limit=limit,
            offset=offset,
            has_more=len(history) == limit
        )
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@app.get("/history/{session_id}", response_model=ChatHistoryListResponse)
async def get_session_history(session_id: str):
    """Get specific session history"""
    try:
        history = await db_manager.get_chat_history(session_id=session_id)
        
        return ChatHistoryListResponse(
            items=[ChatHistoryResponse(**item) for item in history],
            total=len(history),
            limit=len(history),
            offset=0,
            has_more=False
        )
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session history")

@app.get("/stats", response_model=UsageStatsResponse)
async def get_usage_stats():
    """Get usage statistics"""
    try:
        stats = await db_manager.get_usage_stats()
        return UsageStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage statistics")
