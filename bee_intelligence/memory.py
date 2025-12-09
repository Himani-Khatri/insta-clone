import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class ConversationMemory:
    def __init__(self, db_path: str = 'bee.db'):
        self.db_path = db_path

    def store_conversation(self, user_id: int, message: str, response: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO conversation_history (user_id, message, response, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            """, (user_id, message, response))
            conn.commit()
        finally:
            conn.close()

    def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT message, response, timestamp
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'message': row[0],
                    'response': row[1],
                    'timestamp': row[2]
                })
            return conversations
        finally:
            conn.close()

    def get_user_context(self, user_id: int) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user preferences and interaction history
            cursor.execute("""
                SELECT h.username, h.bio, h.skills
                FROM hive h
                WHERE h.id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return {}
                
            return {
                'username': user_data[0],
                'bio': user_data[1],
                'skills': user_data[2],
                'recent_conversations': self.get_recent_conversations(user_id, 5)
            }
        finally:
            conn.close()

    def clear_old_conversations(self, days_old: int = 30) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM conversation_history
                WHERE timestamp < datetime('now', '-? days')
            """, (days_old,))
            conn.commit()
        finally:
            conn.close()