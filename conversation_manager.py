import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

class ConversationManager:
    """Manages multi-turn conversation history, context windows, and user preferences."""
    
    def __init__(self, db_path: str = "travel_scout.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conversations table (sessions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                destination TEXT,
                month TEXT,
                vibes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER DEFAULT 0,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                favorite_vibes TEXT,
                favorite_destinations TEXT,
                include_hotels INTEGER DEFAULT 1,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str) -> bool:
        """Create a new user if not exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def create_conversation(self, user_id: str, conversation_id: str, 
                           destination: str = None, month: str = None, 
                           vibes: List[str] = None) -> bool:
        """Create a new conversation session."""
        try:
            self.create_user(user_id)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            vibes_json = json.dumps(vibes) if vibes else None
            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (conversation_id, user_id, destination, month, vibes)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_id, destination, month, vibes_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return False
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   tokens_used: int = 0) -> bool:
        """Add a message to conversation history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, tokens_used)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, role, content, tokens_used))
            
            # Update conversation last_updated
            cursor.execute("""
                UPDATE conversations SET last_updated = CURRENT_TIMESTAMP
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def get_conversation_history(self, conversation_id: str, 
                                limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve conversation history, optionally limited to recent messages."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("""
                    SELECT role, content, timestamp FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (conversation_id, limit))
            else:
                cursor.execute("""
                    SELECT role, content, timestamp FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """, (conversation_id,))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return messages
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_context_window(self, conversation_id: str, 
                          max_tokens: int = 6000) -> str:
        """Build optimized context window for agent (recent messages up to token limit)."""
        messages = self.get_conversation_history(conversation_id)
        
        context_parts = []
        total_tokens = 0
        
        for msg in reversed(messages):
            msg_tokens = len(msg['content'].split()) * 1.3
            
            if total_tokens + msg_tokens > max_tokens:
                break
            
            role = msg['role'].upper()
            context_parts.append(f"{role}: {msg['content']}")
            total_tokens += msg_tokens
        
        return "\n\n".join(reversed(context_parts))
    
    def update_user_preferences(self, user_id: str, vibes: List[str] = None, 
                               destinations: List[str] = None, 
                               include_hotels: bool = True) -> bool:
        """Learn and store user preferences."""
        try:
            self.create_user(user_id)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            vibes_json = json.dumps(vibes) if vibes else None
            dests_json = json.dumps(destinations) if destinations else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences
                (user_id, favorite_vibes, favorite_destinations, include_hotels)
                VALUES (?, ?, ?, ?)
            """, (user_id, vibes_json, dests_json, int(include_hotels)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Retrieve stored user preferences."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                row_dict = dict(row)
                row_dict['favorite_vibes'] = json.loads(row_dict['favorite_vibes']) if row_dict['favorite_vibes'] else []
                row_dict['favorite_destinations'] = json.loads(row_dict['favorite_destinations']) if row_dict['favorite_destinations'] else []
                row_dict['include_hotels'] = bool(row_dict['include_hotels'])
                return row_dict
            
            return {}
        except Exception as e:
            print(f"Error retrieving preferences: {e}")
            return {}
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve user's conversation history."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id, destination, month, vibes, created_at, last_updated
                FROM conversations
                WHERE user_id = ?
                ORDER BY last_updated DESC
                LIMIT ?
            """, (user_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conv_dict = dict(row)
                conv_dict['vibes'] = json.loads(conv_dict['vibes']) if conv_dict['vibes'] else []
                conversations.append(conv_dict)
            
            conn.close()
            return conversations
        except Exception as e:
            print(f"Error retrieving user conversations: {e}")
            return []
    
    def get_total_tokens_used(self, user_id: str) -> int:
        """Track total API tokens used by user (for cost monitoring)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(tokens_used) as total
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.conversation_id
                WHERE c.user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result[0] else 0
        except Exception as e:
            print(f"Error calculating tokens: {e}")
            return 0
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Remove conversations older than specified days (data hygiene)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM messages WHERE conversation_id IN (
                    SELECT conversation_id FROM conversations
                    WHERE datetime(last_updated) < datetime('now', '-' || ? || ' days')
                )
            """, (days,))
            
            cursor.execute("""
                DELETE FROM conversations
                WHERE datetime(last_updated) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Error cleaning up conversations: {e}")
            return 0
