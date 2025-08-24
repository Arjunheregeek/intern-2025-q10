# Chat Persistence System with REST API

A comprehensive chat system with SQLite persistence, REST API, and real Gemini AI integration with enhanced security features including logging and data protection.

## Overview

This system provides persistent storage for chat interactions with a REST API interface, real Google Gemini AI responses, comprehensive logging, and data security measures.

## Project Structure

```
d:\Downloads\ASSIGN\
├── src/
│   ├── database.py              # SQLite setup, models, operations
│   ├── models.py               # Pydantic models for API
│   ├── api.py                  # FastAPI application with endpoints
│   └── chatbot.py              # Enhanced CLI with Gemini AI integration
├── tests/
│   └── test_api.py             # API endpoint tests
├── data/
│   └── chat_history.db         # SQLite database (generated)
├── logs/
│   └── app.log                 # Application logs (generated)
├── exports/                    # Chat history exports (generated)
├── main.py                     # Combined CLI and API server launcher
├── requirements.txt            # Dependencies
├── .env.example               # API key template
└── README.md                  # This file
```

## Features

- **Real AI Integration**: Google Gemini API with free tier support (`gemini-1.5-flash`)
- **Persistent Storage**: SQLite database with optimized schema
- **REST API**: FastAPI with automatic documentation
- **Security**: Input validation, SQL injection prevention, comprehensive logging
- **Export Functionality**: Save chat history to readable text files
- **Session Management**: Track and analyze conversation sessions

## Installation

```bash
pip install -r requirements.txt
```

### Setup Real AI Integration (Required for AI Responses)

1. **Get a Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Create a new API key (free tier available)

2. **Configure the API Key:**
   ```bash
   # Create a .env file
   copy .env.example .env
   # Edit .env and add: GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Test the Integration:**
   ```bash
   python main.py
   # You should see "Connected to Gemini API (Free Tier)"
   ```

**Without API Key:** The system works with simulated responses (marked as [SIMULATED])
**With API Key:** You get real AI responses from Google's Gemini 1.5 Flash model

## Usage

### Start API Server
```bash
# Start FastAPI server
python main.py --mode api

# Access API documentation
# http://localhost:8000/docs
```

### Run CLI Chat
```bash
# Start interactive chat
python main.py --mode cli
```

### Default Mode
```bash
# Start CLI chat (default)
python main.py
```

## API Endpoints

- `GET /history` - Get paginated chat history
- `GET /history/{session_id}` - Get specific session history
- `GET /stats` - Get usage statistics
- `GET /health` - Health check endpoint

## Database Schema

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    response_time_ms REAL
);

CREATE INDEX idx_timestamp ON chat_history(timestamp DESC);
CREATE INDEX idx_session ON chat_history(session_id);
```

## Security Features

- Input sanitization and validation
- SQL injection prevention with prepared statements
- Rate limiting for API endpoints
- Comprehensive audit logging
- Data encryption for sensitive fields

## Logging

- Application logs in `logs/app.log`
- Request/response logging
- Database operation logging
- Error tracking and monitoring

## Quick Start Guide

### Step 1: Install Dependencies
```bash
# Make sure you're in the project directory
cd d:\Downloads\ASSIGN

# Install required packages
pip install -r requirements.txt
```

### Step 2: Choose Your Mode

#### Option A: Just Chat (Simplest)
```bash
# Start the CLI chatbot - this is the easiest way to begin
python main.py

# Or explicitly specify CLI mode
python main.py --mode cli
```
**What happens**: You get an interactive chat interface that saves all conversations to a database.

#### Option B: Start API Server (For Web Access)
```bash
# Start the REST API server
python main.py --mode api
```
**What happens**: 
- Server starts at http://localhost:8000
- You can view API documentation at http://localhost:8000/docs
- You can make API calls to retrieve chat history

### Step 3: Understanding the Workflow

#### For CLI Chat:
1. Run `python main.py`
2. Type messages and get responses
3. Type `stats` to see session statistics
4. Type `quit` to exit
5. All conversations are automatically saved to the database

#### For API Server:
1. Run `python main.py --mode api`
2. Open browser to http://localhost:8000/docs
3. Test endpoints:
   - `/health` - Check if server is running
   - `/history` - View all chat history
   - `/stats` - See usage statistics
4. Use these endpoints in your web applications

### Step 4: Viewing Your Data

#### Via CLI:
```bash
# Start chat and type 'stats' to see your session data
python main.py
You: stats
```

#### Via API:
```bash
# Start API server
python main.py --mode api

# Then visit these URLs in your browser:
# http://localhost:8000/health
# http://localhost:8000/history
# http://localhost:8000/stats
```

#### Direct Database Access:
Your chat data is stored in `data/chat_history.db` which you can open with any SQLite browser.

## Data Storage & Export

### Where Your Data is Stored
```
d:\Downloads\ASSIGN\data\chat_history.db
```
This SQLite database file contains all your conversations, timestamps, token usage, and response times.

### Export Your Conversations
```bash
# Start the chat and type 'export'
python main.py
You: export
# Creates: exports/chat_history_YYYYMMDD_HHMMSS.txt
```
This creates a human-readable file in the `exports/` folder with all your chat history, including:
- Conversation timestamps
- User prompts and AI responses
- Token usage and response time metrics
- Session information

### View Session Statistics
```bash
# In chat, type 'stats' to see:
You: stats
# Shows: interactions count, total tokens, average response time, AI status
```

## Common Use Cases

### 1. Personal Chat Assistant
```bash
python main.py
# Chat normally, all conversations are saved
```

### 2. Web Application Backend
```bash
python main.py --mode api
# Use the API endpoints in your web/mobile app
```

### 3. Data Analysis
```bash
# Use the /stats endpoint or direct database access
# to analyze chat patterns and usage
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the right directory
cd d:\Downloads\ASSIGN

# Check if requirements are installed
pip list | findstr fastapi
```

### Gemini API Issues

**"models/gemini-pro is not found" Error:**
- Fixed: The system now uses `gemini-1.5-flash` (correct free tier model)

**Free Tier Limits:**
- 15 requests per minute
- 1,500 requests per day
- If exceeded, wait until next day or upgrade to paid plan
- Check usage at: https://makersuite.google.com/app/apikey

**API Key Setup:**
1. Visit: https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env` file: `GEMINI_API_KEY=your_key_here`
4. Restart application

**Real vs Simulated Responses:**
- Real: Shows `[REAL AI in XXXms]` before responses
- Simulated: Shows `[SIMULATED]` in response text

### Database issues
- The `data/` folder and database are created automatically
- Logs are stored in `logs/app.log` for debugging

### Port already in use
- The API server uses port 8000 by default
- If occupied, you'll see an error message
