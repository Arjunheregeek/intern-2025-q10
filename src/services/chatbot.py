import sys
import time
import os
from typing import Optional
from datetime import datetime
import asyncio

from .api_client import GeminiAPIClient
from .cache_manager import LLMCache
from .rate_limiter import RateLimiter
from .memory_manager import MemoryManager

# Database integration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from database import db_manager

import structlog
logger = structlog.get_logger()

class CachedChatbot:
    """CLI chatbot with intelligent caching and all advanced features."""
    
    def __init__(self, api_client: GeminiAPIClient):
        """Initialize chatbot with all components."""
        self.api_client = api_client
        self.cache = LLMCache(maxsize=50, ttl=300)  # 50 entries, 5-minute TTL
        self.rate_limiter = RateLimiter(15, 100)  # 15/min, 100/hour
        self.memory_manager = MemoryManager()
        self.session_id = self._generate_session_id()
        self.is_running = False
        self.message_count = 0
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def display_welcome(self) -> None:
        """Display welcome message with all features."""
        print("\n" + "="*60)
        print("🤖 INTELLIGENT CHATBOT WITH ALL FEATURES")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print("Features:")
        print("  • LRU Cache: 50 entries + 5-minute TTL")
        print("  • Rate Limiting: 15 requests/minute")
        print("  • Memory Management: Automatic optimization")
        print("  • Database: SQLite persistence")
        print("\nAvailable commands:")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'cache' - Show cache statistics")
        print("  • 'clear' - Clear cache")
        print("  • 'demo' - Demo cache behavior with duplicates")
        print("  • 'stats' - Show database statistics")
        print("  • 'export' - Export chat history to file")
        print("  • 'memory' - Show memory usage")
        print("  • 'rate' - Show rate limit status")
        print("\nIdentical prompts will return cached responses!")
        print("="*60)
    
    def display_cache_stats(self) -> None:
        """Display detailed cache statistics."""
        stats = self.cache.get_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"  • Cache hits: {stats['hits']}")
        print(f"  • Cache misses: {stats['misses']}")
        print(f"  • Hit rate: {stats['hit_rate_percent']}%")
        print(f"  • Cache size: {stats['cache_size']}/{stats['max_size']}")
        print(f"  • Evictions: {stats['evictions']}")
        print(f"  • TTL: {stats['ttl_seconds']} seconds")
        print(f"  • Time saved: {stats['total_time_saved_ms']/1000:.1f}s total")
        print(f"  • Avg time saved per hit: {stats['avg_time_saved_per_hit']}ms")
    
    def display_memory_stats(self) -> None:
        """Display memory usage statistics."""
        stats = self.memory_manager.get_memory_usage()
        print(f"\n💾 Memory Statistics:")
        print(f"  • Current usage: {stats['current_mb']:.2f} MB")
        print(f"  • Peak usage: {stats['peak_mb']:.2f} MB")
        print(f"  • Available memory: {stats['available_mb']:.2f} MB")
        if stats.get('gc_collections'):
            print(f"  • GC collections: {stats['gc_collections']}")
    
    def display_rate_limits(self) -> None:
        """Display rate limit statistics."""
        stats = self.rate_limiter.get_stats()
        print(f"\n⚡ Rate Limit Statistics:")
        print(f"  • Requests this minute: {stats['requests_current_minute']}")
        print(f"  • Requests this hour: {stats['requests_current_hour']}")
        print(f"  • Minute limit: {stats['minute_limit']}")
        print(f"  • Hour limit: {stats['hour_limit']}")
        print(f"  • Throttled requests: {stats['throttled_count']}")
    
    async def display_db_stats(self) -> None:
        """Display database statistics."""
        try:
            # Initialize database if not done yet
            await db_manager.initialize()
            
            # Get stats
            stats = await db_manager.get_usage_stats()
            history = await db_manager.get_chat_history(session_id=self.session_id)
            
            print(f"\n🗄️ Database Statistics:")
            print(f"  • Total interactions: {stats['total_interactions']}")
            print(f"  • Unique sessions: {stats['unique_sessions']}")
            print(f"  • Current session: {self.session_id} ({len(history)} messages)")
            print(f"  • Average response time: {stats['average_response_time_ms']:.1f} ms")
            print(f"  • Total tokens used: {stats['total_tokens_used']}")
            print(f"  • Database size: {stats['database_size_mb']:.2f} MB")
        except Exception as e:
            print(f"Error retrieving database stats: {e}")
    
    async def export_chat_history(self) -> None:
        """Export chat history to a file."""
        try:
            # Initialize database if not done yet
            await db_manager.initialize()
            
            # Create exports directory
            os.makedirs('exports', exist_ok=True)
            
            # Get all chat history
            all_history = await db_manager.get_chat_history(limit=1000)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exports/chat_history_{timestamp}.txt"
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CHAT HISTORY EXPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Conversations: {len(all_history)}\n\n")
                
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
            print(f"Error exporting chat history: {e}")
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate AI response with caching, rate limiting, and memory management."""
        start_time = time.time()
        
        # Check memory and optimize if needed
        self.memory_manager.check_and_optimize(self.cache)
        
        # Check rate limits
        if not self.rate_limiter.allow_request():
            return "Rate limit exceeded. Please wait a moment before sending more requests."
        
        # Generate cache key
        cache_key = self.cache.get_cache_key(user_input)
        
        # Try to get from cache first
        cached_response = self.cache.get(cache_key)
        if cached_response:
            response_time = time.time() - start_time
            print(f"⚡ [CACHED in {response_time*1000:.1f}ms]", end=" ")
            return cached_response["response"]
        
        # Cache miss - call API
        try:
            prompt = f"You are a helpful assistant. User said: {user_input}\n\nProvide a helpful response:"
            api_start = time.time()
            response = self.api_client.call_api(prompt)
            api_latency = (time.time() - api_start) * 1000
            
            total_time = time.time() - start_time
            print(f"🔄 [FRESH in {total_time*1000:.1f}ms]", end=" ")
            
            # Cache the response
            cache_data = {
                "response": response,
                "original_latency_ms": api_latency,
                "prompt": user_input
            }
            self.cache.set(cache_key, cache_data)
            
            # Store in database
            asyncio.create_task(self._store_in_database(user_input, response, api_latency))
            
            self.message_count += 1
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _store_in_database(self, prompt: str, response: str, latency_ms: float) -> None:
        """Store interaction in database."""
        try:
            # Calculate tokens (simple estimation)
            tokens_used = len(prompt.split()) + len(response.split())
            
            # Initialize database if not done yet
            await db_manager.initialize()
            
            # Store in database
            await db_manager.store_chat_interaction(
                prompt=prompt,
                response=response,
                session_id=self.session_id,
                tokens_used=tokens_used,
                response_time_ms=latency_ms
            )
        except Exception as e:
            print(f"Error storing in database: {e}")
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit']:
            print("\n👋 Goodbye!")
            return True
        
        elif command == 'cache':
            self.display_cache_stats()
            return True
        
        elif command == 'clear':
            self.cache.clear()
            print("\n🧹 Cache cleared!")
            return True
        
        elif command == 'demo':
            self.demo_cache_behavior()
            return True
        
        elif command == 'memory':
            self.display_memory_stats()
            return True
        
        elif command == 'rate':
            self.display_rate_limits()
            return True
        
        elif command == 'stats':
            # This needs async, so we'll handle it in the main loop
            return True
        
        elif command == 'export':
            # This needs async, so we'll handle it in the main loop
            return True
        
        return False
    
    def demo_cache_behavior(self) -> None:
        """Demo cache behavior with duplicate prompts."""
        print("\n🚀 Cache Demo - Testing duplicate prompts...")
        
        test_prompts = [
            "What is Python?",
            "Tell me about AI",
            "What is Python?",  # Duplicate - should be cached
            "Explain machine learning",
            "Tell me about AI"  # Duplicate - should be cached
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Demo Request {i}: '{prompt}' ---")
            start_time = time.time()
            
            response = self.generate_response(prompt)
            total_time = (time.time() - start_time) * 1000
            
            print(f"\nResponse: {response[:100]}{'...' if len(response) > 100 else ''}")
            print(f"Total time: {total_time:.1f}ms")
            
            time.sleep(0.5)  # Small delay between requests
        
        print("\n" + "="*50)
        self.display_cache_stats()
    
    def run(self) -> None:
        """Start the enhanced chatbot with all features."""
        self.display_welcome()
        self.is_running = True
        
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_async())
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
        
        finally:
            self.is_running = False
            stats = self.cache.get_stats()
            print(f"\nSession Summary:")
            print(f"  • Messages sent: {self.message_count}")
            print(f"  • Cache hit rate: {stats['hit_rate_percent']}%")
            print(f"  • Time saved by caching: {stats['total_time_saved_ms']/1000:.1f}s")
    
    async def _run_async(self) -> None:
        """Async version of run to handle database operations."""
        # Initialize database
        await db_manager.initialize()
        
        while self.is_running:
            try:
                user_input = input(f"\n[Cache: {self.cache.get_stats()['cache_size']}/50] You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Handle special commands
            if self.handle_command(user_input):
                if user_input.lower().strip() in ['quit', 'exit']:
                    break
                
                # Handle async commands
                if user_input.lower() == 'stats':
                    await self.display_db_stats()
                    continue
                elif user_input.lower() == 'export':
                    await self.export_chat_history()
                    continue
                
                continue
            
            # Generate response
            response = self.generate_response(user_input)
            
            if response:
                print(f"\n🤖 AI: {response}")
