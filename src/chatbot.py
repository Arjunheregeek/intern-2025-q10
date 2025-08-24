"""
Enhanced CLI chatbot with database logging, session management, and real Gemini API integration.
Uses the exact working implementation from services/chatbot.py for free tier Gemini API.
"""

import asyncio
import time
import uuid
import logging
import os
from datetime import datetime
from typing import Optional

try:
    from database import db_manager
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Install missing packages: pip install google-generativeai python-dotenv")
    raise

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiAPIClient:
    """Free tier Gemini API client - exact implementation from services"""
    
    def __init__(self):
        self.model = None
        self.initialize()
    
    def initialize(self):
        """Initialize Gemini API for free tier"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("WARNING: No GEMINI_API_KEY found!")
            print("To get real AI responses:")
            print("   1. Get API key: https://makersuite.google.com/app/apikey") 
            print("   2. Create .env file: GEMINI_API_KEY=your_key_here")
            print("   3. Restart the application")
            return False
        
        try:
            genai.configure(api_key=api_key)
            # Use the correct free tier model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("Connected to Gemini API (Free Tier)")
            return True
        except Exception as e:
            print(f"Gemini API initialization failed: {e}")
            return False
    
    def call_api(self, prompt: str) -> str:
        """Call Gemini API - exact implementation from services"""
        if not self.model:
            raise Exception("Gemini API not initialized")
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a proper response."
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")

class EnhancedChatbot:
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.interaction_count = 0
        self.api_client = GeminiAPIClient()
        self.message_count = 0
        
    async def initialize(self):
        """Initialize chatbot with database and Gemini API"""
        await db_manager.initialize()
        logger.info(f"Chatbot initialized with session: {self.session_id}")
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate AI response using exact services implementation"""
        start_time = time.time()
        
        # Try to call real Gemini API first
        if self.api_client.model:
            try:
                prompt = f"You are a helpful assistant. User said: {user_input}\n\nProvide a helpful response:"
                api_start = time.time()
                response = self.api_client.call_api(prompt)
                api_latency = (time.time() - api_start) * 1000
                
                total_time = time.time() - start_time
                print(f"[REAL AI in {total_time*1000:.1f}ms]", end=" ")
                
                self.message_count += 1
                return response, api_latency
                
            except Exception as e:
                print(f"API Error: {str(e)}")
                return self._get_fallback_response(user_input), 100.0
        else:
            # Fallback to simulated responses
            return self._get_fallback_response(user_input), 100.0
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Fallback responses when API is not available"""
        prompt_lower = user_input.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "[SIMULATED] Hello! I'm your AI assistant. Please set up your GEMINI_API_KEY for real AI responses."
        elif "china" in prompt_lower:
            return "[SIMULATED] China is located in East Asia and is the world's most populous country."
        elif "langchain" in prompt_lower:
            return "[SIMULATED] LangChain is a framework for developing applications with large language models."
        else:
            return f"[SIMULATED] I understand you're asking about: {user_input[:50]}. Set up GEMINI_API_KEY for real AI responses."

    async def process_interaction(self, prompt: str) -> str:
        """Process user interaction and store in database"""
        try:
            # Generate response using real AI or simulation
            response, response_time_ms = self.generate_response(prompt)
            
            # Calculate tokens (simple estimation)
            tokens_used = len(prompt.split()) + len(response.split())
            
            # Store in database
            await db_manager.store_chat_interaction(
                prompt=prompt,
                response=response,
                session_id=self.session_id,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms
            )
            
            self.interaction_count += 1
            logger.info(f"Processed interaction {self.interaction_count} in session {self.session_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to process interaction: {e}")
            return "Sorry, I encountered an error processing your request."
    
    def handle_command(self, user_input: str) -> tuple[bool, bool]:
        """Handle special commands from services implementation"""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit']:
            print("\nGoodbye!")
            return True, True  # (is_command, should_exit)
        elif command == 'stats':
            return True, False  # Handle in main loop
        elif command == 'export':
            return True, False  # Handle in main loop
        
        return False, False

    async def run_cli(self):
        """Run interactive CLI chat with services-style interface"""
        await self.initialize()
        
        # Display welcome message similar to services
        print("\n" + "="*60)
        print("Enhanced Chat System with Persistence")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        if self.api_client.model:
            print("Status: Real Gemini AI enabled (Free Tier)")
        else:
            print("Status: Simulated responses (set GEMINI_API_KEY for real AI)")
        print("\nCommands:")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'stats' - Show session statistics")
        print("  • 'export' - Export chat history to file")
        print("="*60)
        
        try:
            while True:
                try:
                    user_input = input(f"\n[Session: {self.session_id}] You: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nGoodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                is_command, should_exit = self.handle_command(user_input)
                if should_exit:
                    break
                elif is_command:
                    # Handle async commands
                    if user_input.lower() == 'stats':
                        await self.show_session_stats()
                    elif user_input.lower() == 'export':
                        await self.export_chat_data()
                    continue
                
                # Process interaction
                response = await self.process_interaction(user_input)
                print(f"\nAI: {response}")
        
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"\nAn unexpected error occurred: {e}")
        
        finally:
            # Session summary similar to services
            print(f"\nSession Summary:")
            print(f"  • Messages sent: {self.message_count}")
            print(f"  • Total interactions: {self.interaction_count}")
            print(f"  • AI Status: {'Real Gemini API' if self.api_client.model else 'Simulated responses'}")

    async def show_session_stats(self):
        """Show current session statistics"""
        try:
            history = await db_manager.get_chat_history(session_id=self.session_id)
            
            if not history:
                print("No interactions in this session yet.")
                return
            
            total_tokens = sum(item.get('tokens_used', 0) for item in history)
            avg_response_time = sum(item.get('response_time_ms', 0) for item in history) / len(history)
            
            print(f"\nSession Statistics:")
            print(f"  • Interactions: {len(history)}")
            print(f"  • Total tokens: {total_tokens}")
            print(f"  • Average response time: {avg_response_time:.1f}ms")
            print(f"  • AI Status: {'Real Gemini API' if self.api_client.model else 'Simulated responses'}")
            
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            print("Unable to retrieve session statistics.")

    async def export_chat_data(self):
        """Export chat data to a readable file"""
        try:
            # Get all chat history
            all_history = await db_manager.get_chat_history(limit=1000)
            
            # Create exports directory
            os.makedirs('exports', exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exports/chat_history_{timestamp}.txt"
            
            # Write data to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CHAT HISTORY EXPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Conversations: {len(all_history)}\n")
                f.write(f"AI Status: {'Real Gemini API' if self.api_client.model else 'Simulated responses'}\n\n")
                
                for i, chat in enumerate(all_history, 1):
                    f.write(f"--- Conversation {i} ---\n")
                    f.write(f"Session: {chat['session_id']}\n")
                    f.write(f"Time: {chat['timestamp']}\n")
                    f.write(f"User: {chat['prompt']}\n")
                    f.write(f"Bot: {chat['response']}\n")
                    f.write(f"Metrics: {chat['tokens_used']} tokens, {chat['response_time_ms']:.1f}ms\n")
                    f.write("\n")
            
            print(f"\nChat history exported to: {filename}")
            print(f"Exported {len(all_history)} conversations")
            
        except Exception as e:
            logger.error(f"Failed to export chat data: {e}")
            print("Failed to export chat data. Check logs for details.")

if __name__ == "__main__":
    chatbot = EnhancedChatbot()
    asyncio.run(chatbot.run_cli())
