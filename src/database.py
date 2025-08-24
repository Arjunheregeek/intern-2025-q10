"""
Database layer with SQLite operations, security, and logging.
"""

import sqlite3
import asyncio
import aiosqlite
import logging
import hashlib
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "data/chat_history.db"):
        self.db_path = db_path
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        logger.info(f"Initializing database manager with path: {db_path}")

    async def initialize(self):
        """Initialize database with schema and indexes"""
        try:
            # Create database file if it doesn't exist
            if not os.path.exists(self.db_path):
                logger.info(f"Creating new database file: {self.db_path}")

            async with aiosqlite.connect(self.db_path) as db:
                await self.create_schema(db)
                await self.create_indexes(db)
                await db.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def create_schema(self, db: aiosqlite.Connection):
        """Create database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            response_time_ms REAL DEFAULT 0.0
        );
        """
        await db.execute(schema_sql)

        # Add new columns if they don't exist (for migration)
        try:
            await db.execute("ALTER TABLE chat_history ADD COLUMN prompt_hash TEXT;")
            logger.info("Added prompt_hash column")
        except Exception:
            pass

        try:
            await db.execute(
                "ALTER TABLE chat_history ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;"
            )
            logger.info("Added created_at column")
        except Exception:
            pass

        logger.info("Database schema created")

    async def create_indexes(self, db: aiosqlite.Connection):
        """Create performance indexes"""
        # Get existing columns to check what indexes we can create
        cursor = await db.execute("PRAGMA table_info(chat_history)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        # Basic indexes that should always work
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id);",
        ]

        # Add conditional indexes based on available columns
        if "prompt_hash" in column_names:
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_prompt_hash ON chat_history(prompt_hash);"
            )

        if "created_at" in column_names:
            indexes.append(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON chat_history(created_at DESC);"
            )

        for index_sql in indexes:
            try:
                await db.execute(index_sql)
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")

        logger.info("Database indexes created")

    def _hash_prompt(self, prompt: str) -> str:
        """Create hash of prompt for deduplication and security"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    def _sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent injection attacks"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        # Remove potential SQL injection patterns
        dangerous_patterns = [";--", "/*", "*/", "xp_", "sp_"]
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")

        return sanitized.strip()

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper error handling"""
        connection = None
        try:
            connection = await aiosqlite.connect(self.db_path)
            connection.row_factory = aiosqlite.Row
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                await connection.close()

    async def store_chat_interaction(
        self,
        prompt: str,
        response: str,
        session_id: str,
        tokens_used: int = 0,
        response_time_ms: float = 0.0,
    ) -> int:
        """Store chat interaction with security measures"""
        try:
            # Sanitize inputs
            prompt = self._sanitize_input(prompt)
            response = self._sanitize_input(response)
            session_id = self._sanitize_input(session_id)

            # Create prompt hash for deduplication
            prompt_hash = self._hash_prompt(prompt)

            async with self.get_connection() as db:
                cursor = await db.execute(
                    """
                    INSERT INTO chat_history 
                    (prompt, response, session_id, tokens_used, response_time_ms, prompt_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        prompt,
                        response,
                        session_id,
                        tokens_used,
                        response_time_ms,
                        prompt_hash,
                    ),
                )

                await db.commit()
                interaction_id = cursor.lastrowid

                logger.info(
                    f"Stored chat interaction: ID={interaction_id}, Session={session_id}"
                )
                return interaction_id

        except Exception as e:
            logger.error(f"Failed to store chat interaction: {e}")
            raise

    async def get_chat_history(
        self, limit: int = 20, offset: int = 0, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get paginated chat history with optional session filtering"""
        try:
            async with self.get_connection() as db:
                if session_id:
                    session_id = self._sanitize_input(session_id)
                    cursor = await db.execute(
                        """
                        SELECT id, prompt, response, tokens_used, timestamp, 
                               session_id, response_time_ms
                        FROM chat_history 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    """,
                        (session_id, limit, offset),
                    )
                else:
                    cursor = await db.execute(
                        """
                        SELECT id, prompt, response, tokens_used, timestamp, 
                               session_id, response_time_ms
                        FROM chat_history 
                        ORDER BY timestamp DESC 
                        LIMIT ? OFFSET ?
                    """,
                        (limit, offset),
                    )

                rows = await cursor.fetchall()
                history = [dict(row) for row in rows]

                logger.info(f"Retrieved {len(history)} chat history entries")
                return history

        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise

    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            async with self.get_connection() as db:
                # Total interactions
                cursor = await db.execute("SELECT COUNT(*) as total FROM chat_history")
                total_row = await cursor.fetchone()
                total_interactions = total_row["total"] if total_row else 0

                # Unique sessions
                cursor = await db.execute(
                    "SELECT COUNT(DISTINCT session_id) as unique_sessions FROM chat_history"
                )
                sessions_row = await cursor.fetchone()
                unique_sessions = sessions_row["unique_sessions"] if sessions_row else 0

                # Average response time
                cursor = await db.execute(
                    "SELECT AVG(response_time_ms) as avg_response_time FROM chat_history WHERE response_time_ms > 0"
                )
                avg_time_row = await cursor.fetchone()
                avg_response_time = (
                    avg_time_row["avg_response_time"] if avg_time_row else 0
                )

                # Total tokens used
                cursor = await db.execute(
                    "SELECT SUM(tokens_used) as total_tokens FROM chat_history"
                )
                tokens_row = await cursor.fetchone()
                total_tokens = tokens_row["total_tokens"] if tokens_row else 0

                stats = {
                    "total_interactions": total_interactions,
                    "unique_sessions": unique_sessions,
                    "average_response_time_ms": (
                        round(avg_response_time, 2) if avg_response_time else 0
                    ),
                    "total_tokens_used": total_tokens,
                    "database_size_mb": await self._get_db_size(),
                }

                logger.info(f"Generated usage stats: {stats}")
                return stats

        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            raise

    async def _get_db_size(self) -> float:
        """Get database file size in MB"""
        try:
            if os.path.exists(self.db_path):
                size_bytes = os.path.getsize(self.db_path)
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except Exception:
            return 0.0

    async def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil

            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
