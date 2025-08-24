"""
Simple script to view what's stored in the chat database.
Run this to see all your saved conversations.
"""

import sqlite3
import os
from datetime import datetime

def view_database_contents():
    """Display all data stored in the chat database"""
    db_path = "data/chat_history.db"
    
    if not os.path.exists(db_path):
        print("❌ No database found. Start chatting first to create data!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all chat history
        cursor.execute("""
            SELECT * FROM chat_history 
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("📭 Database exists but no chat history found.")
            return
        
        print("💬 CHAT DATABASE CONTENTS")
        print("=" * 60)
        print(f"Database Location: {os.path.abspath(db_path)}")
        print(f"Total Conversations: {len(rows)}")
        print(f"Database Size: {os.path.getsize(db_path)} bytes")
        print()
        
        # Show each conversation
        for i, row in enumerate(rows, 1):
            print(f"--- Conversation #{i} ---")
            print(f"ID: {row['id']}")
            print(f"Session: {row['session_id']}")
            print(f"Time: {row['timestamp']}")
            print(f"👤 User: {row['prompt']}")
            print(f"🤖 Bot: {row['response']}")
            print(f"📊 Tokens: {row['tokens_used']}, Response Time: {row['response_time_ms']:.1f}ms")
            print()
        
        # Show statistics
        cursor.execute("SELECT COUNT(DISTINCT session_id) as sessions FROM chat_history")
        unique_sessions = cursor.fetchone()['sessions']
        
        cursor.execute("SELECT SUM(tokens_used) as total_tokens FROM chat_history")
        total_tokens = cursor.fetchone()['total_tokens']
        
        cursor.execute("SELECT AVG(response_time_ms) as avg_time FROM chat_history")
        avg_time = cursor.fetchone()['avg_time']
        
        print("📈 STATISTICS")
        print("-" * 30)
        print(f"Unique Sessions: {unique_sessions}")
        print(f"Total Tokens Used: {total_tokens}")
        print(f"Average Response Time: {avg_time:.1f}ms")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    print("🔍 Chat Database Viewer")
    print("=" * 30)
    view_database_contents()
