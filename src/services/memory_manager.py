"""
Memory manager for monitoring and optimizing memory usage.
"""

import gc
import os
import platform
import time
from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()

class ConversationMemoryManager:
    """Manages conversation memory using LangChain ConversationBufferWindowMemory."""
    
    def __init__(self, window_size: int = 4):
        """
        Initialize memory manager with sliding window.
        
        Args:
            window_size: Number of conversation turns to remember (default: 4)
        """
        self.memory = ConversationBufferWindowMemory(
            k=window_size,  # Keep last 4 turns (8 messages total)
            return_messages=True,
            memory_key="chat_history"
        )
        self.turn_number = 0
        logger.info("Memory manager initialized", window_size=window_size)
    
    def add_user_message(self, message: str) -> None:
        """Add user message to memory."""
        self.memory.chat_memory.add_user_message(message)
        self.turn_number += 1
        logger.debug("User message added", turn=self.turn_number, message_length=len(message))
    
    def add_ai_message(self, message: str) -> None:
        """Add AI response to memory."""
        self.memory.chat_memory.add_ai_message(message)
        logger.debug("AI message added", turn=self.turn_number, message_length=len(message))
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history."""
        messages = self.memory.chat_memory.messages
        history = []
        
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                history.append({
                    "role": "user",
                    "content": msg.content,
                    "turn": (i // 2) + 1
                })
            elif isinstance(msg, AIMessage):
                history.append({
                    "role": "assistant", 
                    "content": msg.content,
                    "turn": (i // 2) + 1
                })
        
        return history
    
    def get_context_for_llm(self) -> str:
        """Get conversation context formatted for LLM prompt."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                context_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context_parts.append(f"Assistant: {msg.content}")
        
        return "\n".join(context_parts)
    
    def clear_memory(self) -> None:
        """Clear all conversation history."""
        old_turn_count = self.turn_number
        self.memory.clear()
        self.turn_number = 0
        logger.info("Memory cleared", previous_turns=old_turn_count)
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory buffer status."""
        messages = self.memory.chat_memory.messages
        return {
            "total_messages": len(messages),
            "conversation_turns": len(messages) // 2,
            "current_turn": self.turn_number,
            "memory_window_size": self.memory.k,
            "is_memory_full": len(messages) >= (self.memory.k * 2)
        }

class MemoryManager:
    """Memory manager for monitoring and optimizing memory usage."""
    
    def __init__(self, threshold_mb: float = 100.0):
        """Initialize memory manager with threshold."""
        self.threshold_mb = threshold_mb
        self.peak_memory_mb = 0.0
        self.last_check_time = time.time()
        self.gc_collections = 0
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # Convert to MB
            current_mb = memory_info.rss / (1024 * 1024)
            
            # Update peak
            if current_mb > self.peak_memory_mb:
                self.peak_memory_mb = current_mb
            
            available_mb = psutil.virtual_memory().available / (1024 * 1024)
            
            return {
                "current_mb": current_mb,
                "peak_mb": self.peak_memory_mb,
                "available_mb": available_mb,
                "gc_collections": self.gc_collections,
                "threshold_mb": self.threshold_mb
            }
        except ImportError:
            # If psutil not available, provide basic info
            return {
                "current_mb": 0.0,
                "peak_mb": self.peak_memory_mb,
                "available_mb": 0.0,
                "gc_collections": self.gc_collections,
                "note": "Install psutil for accurate memory monitoring"
            }
    
    def check_and_optimize(self, cache=None) -> bool:
        """Check memory usage and optimize if needed."""
        # Only check every 10 seconds to avoid overhead
        now = time.time()
        if now - self.last_check_time < 10:
            return False
        
        self.last_check_time = now
        
        # Get memory usage
        stats = self.get_memory_usage()
        
        # Check if above threshold
        if stats["current_mb"] > self.threshold_mb:
            return self.reduce_memory_usage(cache)
        
        return False
    
    def reduce_memory_usage(self, cache=None) -> bool:
        """Reduce memory usage through garbage collection and cache cleanup."""
        # Run garbage collection
        collected = gc.collect()
        self.gc_collections += 1
        
        # Clear cache if provided and still above threshold
        if cache is not None:
            stats_after_gc = self.get_memory_usage()
            
            if stats_after_gc["current_mb"] > self.threshold_mb:
                # Clear half the cache
                cache.clear_oldest(int(cache.get_stats()["cache_size"] / 2))
                return True
        
        return collected > 0
