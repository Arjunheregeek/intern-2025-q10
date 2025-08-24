# Intelligent Chat System with Advanced Features

A comprehensive chat system with SQLite persistence, intelligent LRU caching, rate limiting, memory management, REST API, and Google Gemini AI integration.

## Overview

This production-ready system combines multiple advanced features:
- **Intelligent Caching**: LRU cache with TTL to reduce API calls
- **Rate Limiting**: Prevent API abuse and manage quotas
- **Memory Management**: Monitor and optimize memory usage
- **Database Persistence**: SQLite with optimized schema and indexing
- **REST API**: FastAPI with comprehensive endpoints
- **Real AI**: Google Gemini integration with fallback responses
- **Session Management**: Track and analyze conversation patterns

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
copy .env.example .env
# Edit .env: GEMINI_API_KEY=your_key_here

# 3. Start the intelligent chat system
python main.py
```

## Project Structure

```
d:\Downloads\ASSIGN\
├── src/
│   ├── services/
│   │   ├── chatbot.py         # Cached chatbot with all features
│   │   ├── api_client.py      # Gemini API client
│   │   ├── cache_manager.py   # LRU cache implementation
│   │   ├── rate_limiter.py    # Rate limiter implementation
│   │   └── memory_manager.py  # Memory manager implementation
│   ├── database.py            # Database operations & models
│   ├── models.py              # Pydantic API models
│   └── api.py                 # FastAPI endpoints
├── data/
│   └── chat_history.db        # SQLite database (auto-generated)
├── logs/
│   └── app.log               # Application logs (auto-generated)
├── exports/                   # Chat exports (auto-generated)
├── main.py                   # Unified entry point
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Core Features

### 🧠 Intelligent Caching
- **LRU Cache**: 50 entries with 5-minute TTL
- **Cache Hit Optimization**: Instant responses for repeated queries
- **Smart Eviction**: Automatic cleanup of old entries
- **Statistics**: Hit/miss ratios and performance metrics

### ⚡ Rate Limiting
- **API Protection**: Prevent abuse and quota exhaustion
- **Configurable Limits**: 15 requests/minute, 100/hour
- **Graceful Degradation**: Fallback responses when limited
- **Quota Management**: Smart handling of free tier limits

### 💾 Database Persistence
- **SQLite Storage**: Optimized schema with indexing
- **Session Tracking**: Conversation history and analytics
- **Export Functionality**: Human-readable chat exports
- **Statistics**: Usage metrics and performance data

### 🛠️ Memory Management
- **Automatic Optimization**: Monitors memory usage and clears cache when needed
- **Garbage Collection**: Reduces memory footprint during high usage
- **Statistics**: Tracks current, peak, and available memory

### 🌐 REST API
- **FastAPI Framework**: Auto-generated documentation
- **Rate Limited Endpoints**: Protected API access
- **Health Monitoring**: Service status and diagnostics
- **Metrics Collection**: Performance and usage analytics

## Usage Modes

### 1. Interactive CLI (Primary)
```bash
python main.py
# Features: Real-time chat with caching, rate limiting, memory management, and persistence
```

### 2. API Server
```bash
python main.py --mode api
# Access: http://localhost:8000/docs
```

## Chat Commands

| Command   | Function                                      |
|-----------|----------------------------------------------|
| `cache`   | Show intelligent cache statistics            |
| `clear`   | Clear cache and reset hit/miss ratios        |
| `stats`   | Display session and database statistics      |
| `export`  | Save complete chat history to file           |
| `demo`    | Demonstrate cache behavior with duplicates   |
| `memory`  | Show memory usage statistics                 |
| `rate`    | Show rate limit status                       |
| `quit`    | Exit with session summary                    |

## API Endpoints

| Endpoint           | Method | Features                                   |
|--------------------|--------|-------------------------------------------|
| `/chat`            | POST   | Send message, get AI response             |
| `/history`         | GET    | Paginated chat history with rate limiting |
| `/history/{id}`    | GET    | Retrieve specific session history         |
| `/stats`           | GET    | Comprehensive usage statistics            |
| `/health`          | GET    | Service health with dependency checks     |

## Advanced Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./data/chat_history.db
LOG_LEVEL=INFO
CACHE_SIZE=50
CACHE_TTL=300
RATE_LIMIT_PER_MINUTE=15
RATE_LIMIT_PER_HOUR=100
```

### Cache Configuration
- **Size**: 50 entries (configurable)
- **TTL**: 5 minutes (300 seconds)
- **Eviction**: LRU (Least Recently Used)
- **Key Generation**: SHA-256 hash of prompts

### Rate Limiting
- **Free Tier Safe**: 15 requests/minute, 1,500/day
- **Intelligent Backoff**: Automatic quota management
- **Cache Integration**: Reduces API calls through caching
- **Fallback Responses**: Graceful degradation when limited

### Memory Management
- **Threshold**: Clears cache when memory exceeds 100 MB
- **Garbage Collection**: Runs automatically during high memory usage
- **Statistics**: Tracks current, peak, and available memory

## Performance Features

### Cache Performance
```
Cache Hit Example:
You: What is Python?
🔄 [FRESH in 1247ms] - First request (API call)

You: What is Python?
⚡ [CACHED in 2ms] - Cached response (600x faster!)
```

### Database Optimization
- **Indexed Queries**: Fast retrieval by timestamp and session
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking database calls
- **Migration Support**: Schema updates and backwards compatibility

## Production Deployment

### Docker Support
```bash
# Build optimized container
docker build -t intelligent-chat .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  intelligent-chat
```

### Monitoring & Analytics
- **Real-time Metrics**: Cache hit rates, response times
- **Usage Analytics**: Session patterns, popular queries
- **Health Monitoring**: Database, API, and cache status
- **Export Capabilities**: Complete conversation archives

## Development

### Running Tests
```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run comprehensive tests
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Format code
black src/ --line-length 88

# Lint code
flake8 src/ --max-line-length 88
```

## Troubleshooting

### Common Issues

**Cache Not Working**
- Check memory usage and cache size limits
- Verify TTL settings and expiration

**Rate Limiting Errors**
- Monitor API quota usage
- Adjust rate limits in configuration
- Check cache hit rates to reduce API calls

**Database Issues**
- Verify file permissions in `data/` directory
- Check disk space for database growth
- Review logs for connection errors

### Performance Optimization

**Improve Cache Hit Rate**
- Increase cache size for more entries
- Extend TTL for longer cache retention
- Analyze query patterns for optimization

**Reduce API Usage**
- Enable aggressive caching
- Implement query preprocessing
- Use fallback responses for common queries

## Architecture

The system uses a layered architecture:

1. **Presentation Layer**: CLI interface with rich formatting
2. **Business Logic**: Intelligent caching, rate limiting, and memory management
3. **Data Access**: Async database operations with pooling
4. **External APIs**: Gemini integration with error handling
5. **Infrastructure**: Logging, monitoring, and health checks

## License

MIT License - see LICENSE file for details.
- **Smart Eviction**: Automatic cleanup of old entries
- **Statistics**: Hit/miss ratios and performance metrics

### 💾 Database Persistence
- **SQLite Storage**: Optimized schema with indexing
- **Session Tracking**: Conversation history and analytics
- **Export Functionality**: Human-readable chat exports
- **Statistics**: Usage metrics and performance data

### 🌐 REST API
- **FastAPI Framework**: Auto-generated documentation
- **Rate Limited Endpoints**: Protected API access
- **Health Monitoring**: Service status and diagnostics
- **Metrics Collection**: Performance and usage analytics

## Usage Modes

### 1. Interactive CLI (Primary)
```bash
python main.py
# Features: Real-time chat with caching, rate limiting, and persistence
```

### 2. API Server
```bash
python main.py --mode api
# Access: http://localhost:8000/docs
```

## Chat Commands

| Command | Function |
|---------|----------|
| `cache` | Show intelligent cache statistics |
| `clear` | Clear cache and reset hit/miss ratios |
| `stats` | Display session and database statistics |
| `export` | Save complete chat history to file |
| `demo` | Demonstrate cache behavior with duplicates |
| `quit` | Exit with session summary |

## API Endpoints

| Endpoint | Method | Features |
|----------|--------|----------|
| `/history` | GET | Paginated chat history with rate limiting |
| `/history/{session_id}` | GET | Session-specific conversation data |
| `/stats` | GET | Comprehensive usage statistics |
| `/health` | GET | Service health with dependency checks |

## Advanced Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./data/chat_history.db
LOG_LEVEL=INFO
CACHE_SIZE=50
CACHE_TTL=300
RATE_LIMIT_PER_MINUTE=15
RATE_LIMIT_PER_HOUR=100
```

### Cache Configuration
- **Size**: 50 entries (configurable)
- **TTL**: 5 minutes (300 seconds)
- **Eviction**: LRU (Least Recently Used)
- **Key Generation**: SHA-256 hash of prompts

### Rate Limiting
- **Free Tier Safe**: 15 requests/minute, 1,500/day
- **Intelligent Backoff**: Automatic quota management
- **Cache Integration**: Reduces API calls through caching
- **Fallback Responses**: Graceful degradation when limited

## Performance Features

### Cache Performance
```
Cache Hit Example:
You: What is Python?
🔄 [FRESH in 1247ms] - First request (API call)

You: What is Python?
⚡ [CACHED in 2ms] - Cached response (600x faster!)
```

### Database Optimization
- **Indexed Queries**: Fast retrieval by timestamp and session
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking database calls
- **Migration Support**: Schema updates and backwards compatibility

## Production Deployment

### Docker Support
```bash
# Build optimized container
docker build -t intelligent-chat .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  intelligent-chat
```

### Monitoring & Analytics
- **Real-time Metrics**: Cache hit rates, response times
- **Usage Analytics**: Session patterns, popular queries
- **Health Monitoring**: Database, API, and cache status
- **Export Capabilities**: Complete conversation archives

## Development

### Running Tests
```bash
# Install development dependencies
pip install pytest pytest-asyncio

# Run comprehensive tests
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Format code
black src/ --line-length 88

# Lint code
flake8 src/ --max-line-length 88
```

## Troubleshooting

### Common Issues

**Cache Not Working**
- Check memory usage and cache size limits
- Verify TTL settings and expiration

**Rate Limiting Errors**
- Monitor API quota usage
- Adjust rate limits in configuration
- Check cache hit rates to reduce API calls

**Database Issues**
- Verify file permissions in `data/` directory
- Check disk space for database growth
- Review logs for connection errors

### Performance Optimization

**Improve Cache Hit Rate**
- Increase cache size for more entries
- Extend TTL for longer cache retention
- Analyze query patterns for optimization

**Reduce API Usage**
- Enable aggressive caching
- Implement query preprocessing
- Use fallback responses for common queries

## Architecture

The system uses a layered architecture:

1. **Presentation Layer**: CLI interface with rich formatting
2. **Business Logic**: Intelligent caching and rate limiting
3. **Data Access**: Async database operations with pooling
4. **External APIs**: Gemini integration with error handling
5. **Infrastructure**: Logging, monitoring, and health checks

## License

MIT License - see LICENSE file for details.
