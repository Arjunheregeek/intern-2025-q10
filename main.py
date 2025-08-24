"""
Combined launcher for CLI chat and API server modes.
"""

import argparse
import asyncio
import logging
import os
import sys
import uvicorn

# Create necessary directories first
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import after path setup
try:
    from src.chatbot import EnhancedChatbot
except ImportError as e:
    print(f"Error importing chatbot: {e}")
    print("Make sure all files are properly created in the src directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_api_server():
    """Run FastAPI server"""
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

async def run_cli_chat():
    """Run CLI chatbot"""
    logger.info("Starting CLI chatbot...")
    chatbot = EnhancedChatbot()
    await chatbot.run_cli()

def main():
    parser = argparse.ArgumentParser(description="Chat Persistence System")
    parser.add_argument("--mode", choices=["api", "cli"], default="cli",
                       help="Run mode: api server or cli chat")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        run_api_server()
    else:
        asyncio.run(run_cli_chat())

if __name__ == "__main__":
    main()
