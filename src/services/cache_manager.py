import hashlib
import time
from typing import Dict, Any, Optional
from cachetools import TTLCache  # Use the actual cachetools library
import threading
import structlog

logger = structlog.get_logger()

class LLMCache:
    """LRU cache with TTL for LLM responses using cachetools."""
    
    def __init__(self, maxsize: int = 50, ttl: int = 300):
        """
        Initialize cache with TTL using cachetools.
        
        Args:
            maxsize: Maximum number of entries (default: 50)
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        """
        # Use cachetools TTLCache instead of custom implementation
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
            "cache_saves_ms": 0  # Total time saved by cache hits
        }
        self.maxsize = maxsize
        self.ttl = ttl
        
        logger.info("LLM Cache initialized with cachetools", maxsize=maxsize, ttl_seconds=ttl)
    
    def get_cache_key(self, prompt: str, **kwargs) -> str:
        """
        Generate cache key from prompt and parameters.
        
        Args:
            prompt: The LLM prompt
            **kwargs: Additional parameters that affect the response
            
        Returns:
            Hashed cache key
        """
        # Combine prompt with sorted parameters for consistent hashing
        cache_data = prompt
        if kwargs:
            params_str = "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_data = f"{prompt}|{params_str}"
        
        # Generate SHA-256 hash for cache key
        return hashlib.sha256(cache_data.encode('utf-8')).hexdigest()[:16]
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response.
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            Cached response dict or None if not found/expired
        """
        with self.lock:
            self.stats["total_requests"] += 1
            
            try:
                cached_entry = self.cache[cache_key]
                self.stats["hits"] += 1
                
                # Calculate time saved (assume average API call is 2 seconds)
                time_saved = cached_entry.get("original_latency_ms", 2000)
                self.stats["cache_saves_ms"] += time_saved
                
                logger.info("Cache hit", 
                           cache_key=cache_key,
                           age_seconds=time.time() - cached_entry["cached_at"])
                
                return cached_entry
                
            except KeyError:
                self.stats["misses"] += 1
                logger.debug("Cache miss", cache_key=cache_key)
                return None
    
    def set(self, cache_key: str, response_data: Dict[str, Any]) -> None:
        """
        Store response in cache.
        
        Args:
            cache_key: Cache key
            response_data: Response data to cache
        """
        with self.lock:
            # Check if we're evicting an entry
            if len(self.cache) >= self.maxsize and cache_key not in self.cache:
                self.stats["evictions"] += 1
            
            # Add metadata to cached entry
            cache_entry = {
                **response_data,
                "cached_at": time.time(),
                "cache_key": cache_key
            }
            
            self.cache[cache_key] = cache_entry
            
            logger.info("Response cached", 
                       cache_key=cache_key,
                       response_length=len(response_data.get("response", "")))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = (self.stats["hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
            
            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "total_requests": self.stats["total_requests"],
                "hit_rate_percent": round(hit_rate, 1),
                "cache_size": len(self.cache),
                "max_size": self.maxsize,
                "ttl_seconds": self.ttl,
                "total_time_saved_ms": self.stats["cache_saves_ms"],
                "avg_time_saved_per_hit": round(self.stats["cache_saves_ms"] / max(1, self.stats["hits"]), 1)
            }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            old_size = len(self.cache)
            self.cache.clear()
            logger.info("Cache cleared", entries_removed=old_size)
    
    def set(self, cache_key: str, response_data: Dict[str, Any]) -> None:
        """
        Store response in cache.
        
        Args:
            cache_key: Cache key
            response_data: Response data to cache
        """
        with self.lock:
            # Check if we're evicting an entry
            if len(self.cache) >= self.maxsize and cache_key not in self.cache:
                self.stats["evictions"] += 1
            
            # Add metadata to cached entry
            cache_entry = {
                **response_data,
                "cached_at": time.time(),
                "cache_key": cache_key
            }
            
            self.cache[cache_key] = cache_entry
            
            logger.info("Response cached", 
                       cache_key=cache_key,
                       response_length=len(response_data.get("response", "")))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            hit_rate = (self.stats["hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
            
            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "total_requests": self.stats["total_requests"],
                "hit_rate_percent": round(hit_rate, 1),
                "cache_size": len(self.cache),
                "max_size": self.maxsize,
                "ttl_seconds": self.ttl,
                "total_time_saved_ms": self.stats["cache_saves_ms"],
                "avg_time_saved_per_hit": round(self.stats["cache_saves_ms"] / max(1, self.stats["hits"]), 1)
            }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            old_size = len(self.cache)
            self.cache.clear()
            logger.info("Cache cleared", entries_removed=old_size)
    
    def cleanup_expired(self) -> int:
        """
        Manually cleanup expired entries.
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            initial_size = len(self.cache)
            # TTLCache automatically removes expired entries on access
            # Force cleanup by accessing cache data
            _ = dict(self.cache)
            removed = initial_size - len(self.cache)
            
            if removed > 0:
                logger.info("Expired entries cleaned up", entries_removed=removed)
            
            return removed
