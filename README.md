# CLI Chatbot with Token Bucket Rate Limiting

An interactive command-line chatbot with token bucket rate limiting that enforces 10 requests per minute to prevent API abuse and manage costs.

## Features

- 🪣 **Token Bucket Rate Limiting**: 10 requests per minute with automatic token refill
- 💬 **Interactive CLI**: Continuous conversation loop with real-time token status
- ⚠️ **Rate Limit Enforcement**: HTTP 429-style blocking when limits exceeded
- 📊 **Status Monitoring**: Real-time bucket status and token availability
- 🛠️ **Demo Commands**: Built-in commands to test rate limiting behavior

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

```bash
python main.py
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `quit` or `exit` | End the conversation |
| `status` | Show rate limit and token bucket status |
| `rapid` | Demo rapid requests to trigger rate limiting |

## Example Session

```
🤖 RATE LIMITED CHATBOT
============================================================
Rate limit: 10 messages per minute

[Tokens: 10] You: Hello!
🤖 AI: Hello! How can I help you today?

[Tokens: 9] You: status
📊 Rate Limit Status:
  • Remaining requests: 9
  • Limit per minute: 10
  • Next token in: 0.0s
  • Request allowed: ✅ Yes
  • Bucket tokens: 9.0/10
  • Refill rate: 10.0 tokens/min

[Tokens: 9] You: rapid
🚀 Rapid Request Demo (testing rate limits)...

Request 1: ✅ Allowed
Request 2: ✅ Allowed  
Request 3: ✅ Allowed
Request 4: ❌ Rate limited (wait 2.1s)
Request 5: ❌ Rate limited (wait 1.6s)
```

## Token Bucket Algorithm

### Configuration
- **Bucket Capacity**: 10 tokens
- **Refill Rate**: 10 tokens per 60 seconds (1 token every 6 seconds)
- **Request Cost**: 1 token per chat message
- **Thread Safety**: Uses threading.Lock() for concurrent access

### Rate Limiting Behavior
1. **Full Bucket**: Starts with 10/10 tokens available
2. **Token Consumption**: Each message consumes 1 token
3. **Automatic Refill**: Tokens refill at steady rate (10/minute)
4. **Rate Limiting**: Blocks requests when bucket is empty
5. **Recovery**: Automatic recovery as tokens refill

## Architecture

```
src/
├── services/
│   ├── rate_limiter.py      # Token bucket implementation
│   ├── chatbot.py          # Rate limited CLI interface
│   └── api_client.py       # Gemini API client
tests/
├── test_rate_limiter.py    # Rate limiting tests
main.py                     # Entry point
```

## Testing

```bash
# Run rate limiting tests
pytest tests/test_rate_limiter.py -v

# Test concurrent access
pytest tests/test_rate_limiter.py::TestTokenBucket::test_concurrent_access -v
```

## Rate Limiting States

| State | Token Count | Behavior |
|-------|-------------|----------|
| **Full** | 10/10 | All requests allowed |
| **Partial** | 1-9/10 | Requests allowed, showing countdown |
| **Empty** | 0/10 | Requests blocked with wait time |
| **Refilling** | Increasing | Automatic token recovery |

## Error Handling

- **Rate Limit Exceeded**: Clear error message with wait time
- **API Failures**: Error displayed, tokens not consumed
- **Invalid Commands**: Helpful command suggestions
- **Graceful Exit**: Ctrl+C handling with usage statistics

## Implementation Details

### Token Bucket Class
```python
class TokenBucket:
    def __init__(self, capacity=10, refill_rate=10/60):
        # Thread-safe token bucket with configurable limits
    
    def consume(self, tokens=1) -> bool:
        # Returns True if tokens available, False if rate limited
    
    def get_status(self) -> dict:
        # Returns current tokens, capacity, next_refill_time
```

### Rate Limiter Integration
- Checks token availability before API calls
- Displays remaining tokens in chat prompt
- Automatic retry suggestions when rate limited
- Real-time status updates
