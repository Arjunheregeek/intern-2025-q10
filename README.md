# CLI Chatbot with Intelligent LRU Caching

An interactive command-line chatbot with intelligent caching using LRU (Least Recently Used) algorithm and TTL (Time To Live) to reduce duplicate LLM API calls and improve response times.

## Features

- 🧠 **LRU Cache with TTL**: 50 entries maximum, 5-minute expiration
- ⚡ **Performance Optimization**: Instant responses for cached prompts
- 📊 **Cache Analytics**: Hit/miss ratios, time savings, performance metrics
- 🔄 **Automatic Cleanup**: Expired entry removal and memory management
- 💾 **Smart Key Generation**: Hash-based keys for consistent caching

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
| `cache` | Show detailed cache statistics |
| `clear` | Clear all cached entries |
| `demo` | Demonstrate cache behavior with duplicate prompts |

## Example Session

```
🤖 INTELLIGENT CACHED CHATBOT
============================================================
Features: LRU Cache (50 entries) + 5-minute TTL

[Cache: 0/50] You: What is Python?
🔄 [FRESH in 1247.3ms] 
🤖 AI: Python is a high-level programming language...

[Cache: 1/50] You: What is Python?
⚡ [CACHED in 2.1ms] 
🤖 AI: Python is a high-level programming language...

[Cache: 1/50] You: cache
📊 Cache Statistics:
  • Cache hits: 1
  • Cache misses: 1
  • Hit rate: 50.0%
  • Cache size: 1/50
  • Time saved: 1.2s total
  • Avg time saved per hit: 1247.3ms
```

## Caching Strategy

### LRU Algorithm with TTL
- **Cache Size**: 50 entries maximum
- **TTL**: 5 minutes (300 seconds)
- **Eviction**: Least Recently Used entries removed when full
- **Key Generation**: SHA-256 hash of prompt + parameters

### Performance Benefits
1. **Instant Responses**: Cached prompts return in ~2ms vs ~1200ms fresh
2. **API Cost Reduction**: Eliminates duplicate API calls
3. **Bandwidth Savings**: Reduces network requests
4. **User Experience**: Faster responses for repeated queries

## Cache Implementation

### Key Generation
```python
def get_cache_key(self, prompt: str, **kwargs) -> str:
    # SHA-256 hash of prompt + sorted parameters
    cache_data = f"{prompt}|{sorted_params}"
    return hashlib.sha256(cache_data.encode()).hexdigest()[:16]
```

### Cache Entry Structure
```python
{
    "response": "LLM response text",
    "cached_at": 1640995200.0,
    "original_latency_ms": 1247.3,
    "cache_key": "a1b2c3d4e5f6g7h8"
}
```

## Architecture

```
src/
├── services/
│   ├── cache_manager.py    # LRU cache with TTL implementation
│   ├── chatbot.py         # Cached chatbot interface
│   └── api_client.py      # Gemini API client
tests/
├── test_cache.py          # Cache functionality tests
main.py                    # Entry point
```

## Performance Metrics

### Cache Statistics
- **Hit Rate**: Percentage of requests served from cache
- **Response Time**: Fresh vs cached comparison
- **Memory Usage**: Current cache size and capacity
- **Time Savings**: Total milliseconds saved by caching

### Cache States
| State | Description | Behavior |
|-------|-------------|----------|
| **Empty** | 0/50 entries | All requests fresh, building cache |
| **Building** | 1-49/50 | Mix of fresh and cached responses |
| **Full** | 50/50 | LRU eviction on new unique prompts |
| **Expired** | TTL exceeded | Automatic cleanup on access |

## Testing

```bash
# Run cache tests
pytest tests/test_cache.py -v

# Test TTL expiration
pytest tests/test_cache.py::TestLLMCache::test_ttl_expiration -v

# Test LRU eviction
pytest tests/test_cache.py::TestLLMCache::test_lru_eviction -v
```

## Cache Demo

The `demo` command shows caching in action:

```bash
[Cache: 0/50] You: demo

🚀 Cache Demo - Testing duplicate prompts...

--- Demo Request 1: 'What is Python?' ---
🔄 [FRESH in 1247.3ms] 
Response: Python is a high-level programming language...

--- Demo Request 2: 'Tell me about AI' ---
🔄 [FRESH in 1156.7ms] 
Response: AI (Artificial Intelligence) refers to...

--- Demo Request 3: 'What is Python?' ---
⚡ [CACHED in 2.1ms] 
Response: Python is a high-level programming language...

📊 Cache Statistics:
  • Hit rate: 33.3%
  • Time saved: 1.2s total
```

## Error Handling

- **Cache Failures**: Graceful fallback to fresh API calls
- **TTL Expiration**: Automatic refresh of stale entries
- **Memory Management**: LRU eviction prevents memory overflow
- **Thread Safety**: Concurrent access protection with locks
