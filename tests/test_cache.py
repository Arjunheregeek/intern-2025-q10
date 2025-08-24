import pytest
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.cache_manager import LLMCache  # Ensure this import matches your project structure

class TestLLMCache:
    """Test LLM cache functionality."""
    
    def test_cache_initialization(self):
        """Test cache initializes correctly."""
        cache = LLMCache(maxsize=10, ttl=60)
        stats = cache.get_stats()
        
        assert stats['max_size'] == 10
        assert stats['ttl_seconds'] == 60
        assert stats['cache_size'] == 0
        assert stats['hit_rate_percent'] == 0
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        cache = LLMCache()
        
        # Same prompt should generate same key
        key1 = cache.get_cache_key("Hello world")
        key2 = cache.get_cache_key("Hello world")
        assert key1 == key2
        
        # Different prompts should generate different keys
        key3 = cache.get_cache_key("Different prompt")
        assert key1 != key3
        
        # Parameters should affect key
        key4 = cache.get_cache_key("Hello", param1="value1")
        key5 = cache.get_cache_key("Hello", param1="value2")
        assert key4 != key5
    
    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        cache = LLMCache(maxsize=5, ttl=60)
        
        # Test cache miss
        key = cache.get_cache_key("test prompt")
        result = cache.get(key)
        assert result is None
        
        # Test cache set and hit
        response_data = {"response": "test response", "tokens": 10}
        cache.set(key, response_data)
        
        cached = cache.get(key)
        assert cached is not None
        assert cached["response"] == "test response"
        assert "cached_at" in cached
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = LLMCache(maxsize=5, ttl=1)  # 1 second TTL
        
        key = cache.get_cache_key("ttl test")
        cache.set(key, {"response": "will expire"})
        
        # Should be cached immediately
        result = cache.get(key)
        assert result is not None
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        result = cache.get(key)
        assert result is None
    
    def test_lru_eviction(self):
        """Test LRU eviction behavior."""
        cache = LLMCache(maxsize=3, ttl=60)
        
        # Fill cache to capacity
        for i in range(3):
            key = cache.get_cache_key(f"prompt {i}")
            cache.set(key, {"response": f"response {i}"})
        
        assert cache.get_stats()['cache_size'] == 3
        
        # Add one more - should evict oldest
        key4 = cache.get_cache_key("prompt 4")
        cache.set(key4, {"response": "response 4"})
        
        # Should still be size 3
        assert cache.get_stats()['cache_size'] == 3
        assert cache.get_stats()['evictions'] == 1
    
    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache = LLMCache(maxsize=5, ttl=60)
        
        key1 = cache.get_cache_key("prompt 1")
        key2 = cache.get_cache_key("prompt 2")
        
        # Generate misses
        cache.get(key1)
        cache.get(key2)
        
        # Set and generate hits
        cache.set(key1, {"response": "response 1"})
        cache.get(key1)
        cache.get(key1)
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['total_requests'] == 4
        assert stats['hit_rate_percent'] == 50.0
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = LLMCache(maxsize=5, ttl=60)
        
        # Add some entries
        for i in range(3):
            key = cache.get_cache_key(f"prompt {i}")
            cache.set(key, {"response": f"response {i}"})
        
        assert cache.get_stats()['cache_size'] == 3
        
        # Clear cache
        cache.clear()
        
        assert cache.get_stats()['cache_size'] == 0
