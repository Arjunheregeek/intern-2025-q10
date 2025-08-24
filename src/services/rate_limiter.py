"""
Rate limiter for API protection and quota management.
"""

import time
from typing import Dict, Any
import threading


class RateLimiter:
    """Rate limiter to protect API endpoints and manage quotas."""

    def __init__(self, minute_limit: int = 15, hour_limit: int = 100):
        """Initialize rate limiter with limits."""
        self.minute_limit = minute_limit
        self.hour_limit = hour_limit
        self.minute_requests = []  # Store timestamps as floats
        self.hour_requests = []  # Store timestamps as floats
        self.throttled_count = 0
        self.cache_hits = 0
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        """Check if request is allowed based on rate limits."""
        with self.lock:
            now = time.time()

            # Clean old requests
            self.minute_requests = [
                t for t in self.minute_requests if now - t < 60
            ]  # 60 seconds in a minute
            self.hour_requests = [
                t for t in self.hour_requests if now - t < 3600
            ]  # 3600 seconds in an hour

            # Check limits
            if len(self.minute_requests) >= self.minute_limit:
                self.throttled_count += 1
                return False

            if len(self.hour_requests) >= self.hour_limit:
                self.throttled_count += 1
                return False

            # Record request
            self.minute_requests.append(now)
            self.hour_requests.append(now)
            return True

    def record_cache_hit(self) -> None:
        """Record a cache hit which doesn't count against rate limits."""
        with self.lock:
            self.cache_hits += 1

    def record_request(self) -> None:
        """Record a successful request."""
        # Already recorded in allow_request
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        with self.lock:
            now = time.time()

            # Clean old requests
            self.minute_requests = [t for t in self.minute_requests if now - t < 60]
            self.hour_requests = [t for t in self.hour_requests if now - t < 3600]

            return {
                "requests_current_minute": len(self.minute_requests),
                "requests_current_hour": len(self.hour_requests),
                "minute_limit": self.minute_limit,
                "hour_limit": self.hour_limit,
                "throttled_count": self.throttled_count,
                "cache_hits": self.cache_hits,
            }
