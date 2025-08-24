import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.services.rate_limiter import RateLimiter

@pytest.fixture
def rate_limiter():
    """Fixture to create a RateLimiter instance."""
    return RateLimiter(minute_limit=5, hour_limit=10)

def test_allow_requests_within_limits(rate_limiter):
    """Test that requests within the rate limits are allowed."""
    for _ in range(5):
        assert rate_limiter.allow_request() is True

def test_deny_requests_exceeding_minute_limit(rate_limiter):
    """Test that requests exceeding the minute limit are denied."""
    for _ in range(5):
        rate_limiter.allow_request()
    assert rate_limiter.allow_request() is False

def test_deny_requests_exceeding_hour_limit(rate_limiter):
    """Test that requests exceeding the hour limit are denied."""
    for _ in range(10):
        rate_limiter.allow_request()
    assert rate_limiter.allow_request() is False

def test_allow_requests_after_time_window(rate_limiter, monkeypatch):
    """Test that requests are allowed after the time window resets."""
    import time
    for _ in range(5):
        rate_limiter.allow_request()
    original_time = time.time
    monkeypatch.setattr(time, "time", lambda: original_time() + 61)  # Use original_time to avoid recursion
    assert rate_limiter.allow_request() is True

def test_rate_limiter_statistics(rate_limiter):
    """Test that the rate limiter statistics are accurate."""
    for _ in range(3):
        rate_limiter.allow_request()
    stats = rate_limiter.get_stats()
    assert stats["requests_current_minute"] == 3
    assert stats["requests_current_hour"] == 3

def test_rate_limiter_throttling(rate_limiter):
    """Test that the throttling count increases when requests are denied."""
    for _ in range(5):
        rate_limiter.allow_request()
    rate_limiter.allow_request()  # This request should be denied
    stats = rate_limiter.get_stats()
    assert stats["throttled_count"] == 1