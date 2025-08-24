import sys
import time
from typing import Optional
from .api_client import GeminiAPIClient
from .cache_manager import LLMCache
import structlog

logger = structlog.get_logger()

class CachedChatbot:
    """CLI chatbot with intelligent caching."""
    
    def __init__(self, api_client: GeminiAPIClient):
        """Initialize chatbot with cache."""
        self.api_client = api_client
        self.cache = LLMCache(maxsize=50, ttl=300)  # 50 entries, 5-minute TTL
        self.is_running = False
        self.message_count = 0
    
    def display_welcome(self) -> None:
        """Display welcome message with cache info."""
        print("\n" + "="*60)
        print("🤖 INTELLIGENT CACHED CHATBOT")
        print("="*60)
        print("Features: LRU Cache (50 entries) + 5-minute TTL")
        print("\nAvailable commands:")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'cache' - Show cache statistics")
        print("  • 'clear' - Clear cache")
        print("  • 'demo' - Demo cache behavior with duplicate prompts")
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
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate AI response with caching."""
        start_time = time.time()
        
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
            
            self.message_count += 1
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
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
        """Start the cached chatbot."""
        self.display_welcome()
        self.is_running = True
        
        try:
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
                    continue
                
                # Generate response
                response = self.generate_response(user_input)
                
                if response:
                    print(f"\n🤖 AI: {response}")
        
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
        
        finally:
            self.is_running = False
            stats = self.cache.get_stats()
            print(f"\nSession Summary:")
            print(f"  • Messages sent: {self.message_count}")
            print(f"  • Cache hit rate: {stats['hit_rate_percent']}%")
            print(f"  • Time saved by caching: {stats['total_time_saved_ms']/1000:.1f}s")
