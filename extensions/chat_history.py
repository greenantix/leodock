import sqlite3
import json
from datetime import datetime
from typing import List, Dict

class ChatHistoryManager:
    def __init__(self, db_path="data/conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for conversation storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                llm_analysis TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                embedding_vector TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp);
            CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id);
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, prompt: str, response: str, session_id: str = None, 
                         llm_analysis: Dict = None, metadata: Dict = None):
        """Save a conversation to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, session_id, prompt, response, llm_analysis, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            session_id,
            prompt,
            response,
            json.dumps(llm_analysis) if llm_analysis else None,
            json.dumps(metadata) if metadata else None
        ))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def search_conversations(self, query: str, limit: int = 50) -> List[Dict]:
        """Search conversations by text content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, session_id, prompt, response, metadata
            FROM conversations 
            WHERE prompt LIKE ? OR response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'session_id': row[2],
                'prompt': row[3],
                'response': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            })
        
        conn.close()
        return results