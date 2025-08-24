import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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
    original_time = time.time  # Save the original time function
    for _ in range(5):
        rate_limiter.allow_request()
    monkeypatch.setattr(time, "time", lambda: original_time() + 61)  # Simulate time passage
    assert rate_limiter.allow_request() is True