import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.services.rate_limiter import RateLimiter

@pytest.fixture
def rate_limiter():
    """Fixture to create a RateLimiter instance."""
    return RateLimiter(minute_limit=5, hour_limit=10)

def test_integration_rate_limiter(rate_limiter):
    """Integration test to simulate multiple components interacting with the RateLimiter."""
    # Simulate multiple requests from different components
    for _ in range(3):
        assert rate_limiter.allow_request() is True

    # Exceed the limit
    for _ in range(2):
        rate_limiter.allow_request()
    assert rate_limiter.allow_request() is False

    # Simulate time passage and retry
    import time
    time.sleep(61)  # Wait for the time window to reset
    assert rate_limiter.allow_request() is True