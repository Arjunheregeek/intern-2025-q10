import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.api_client import GeminiAPIClient
from src.services.chatbot import CachedChatbot

def main():
    """Start the cached chatbot demo."""
    try:
        print("🚀 Starting Intelligent Cached Chatbot Demo")
        
        # Initialize API client
        api_client = GeminiAPIClient()
        
        # Create cached chatbot
        chatbot = CachedChatbot(api_client)
        
        # Run chatbot
        chatbot.run()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
