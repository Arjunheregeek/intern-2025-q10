"""
Entry point for the Intelligent Chat System with all advanced features.
"""

import asyncio
import logging
import os
import sys
import argparse

# Create necessary directories
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

def run_cached_chatbot():
    """Run the CachedChatbot with all features"""
    try:
        # Import here to avoid circular imports
        from src.services.api_client import GeminiAPIClient
        from src.services.chatbot import CachedChatbot
        
        # Initialize API client
        api_client = GeminiAPIClient()
        
        # Create chatbot with all features
        chatbot = CachedChatbot(api_client)
        
        # Run the chatbot
        logger.info("Starting enhanced chatbot with all features...")
        chatbot.run()
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print(f"Error: {e}")
        print("Make sure all required packages are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running chatbot: {e}")
        print(f"Error: {e}")

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Intelligent Chat System with All Features"
    )
    parser.add_argument(
        "--mode", 
        choices=["cli", "api"], 
        default="cli",
        help="Run mode: cli (interactive chat) or api (REST server)"
    )
    
    args = parser.parse_args()
    
    print("\nIntelligent Chat System with Advanced Features")
    print("=" * 50)
    print("Features: LRU Cache + Rate Limiting + Memory Management + Database")
    
    if args.mode == "api":
        print("Starting API server...")
        run_api_server()
    else:
        print("Starting interactive chatbot...")
        run_cached_chatbot()

if __name__ == "__main__":
    main()
