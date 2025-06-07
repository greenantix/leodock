import sqlite3
import json
import pickle
from datetime import datetime
from typing import List, Dict, Optional
import requests

class ChatHistoryManager:
    def __init__(self, db_path="data/conversations.db"):
        self.db_path = db_path
        self.base_url = "http://127.0.0.1:1234/v1"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for conversation storage"""
        # Ensure data directory exists
        import os
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main conversations table
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
        
        # Embeddings table for semantic search
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                embedding_vector BLOB NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Search index for text-based search
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                term_frequency INTEGER DEFAULT 1,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_token ON search_index(token)')
        
        conn.commit()
        conn.close()
        print("📊 Chat history database initialized successfully!")
    
    def store_conversation(self, prompt: str, response: str, session_id: str = None, 
                          llm_analysis: Dict = None, metadata: Dict = None) -> int:
        """Store a conversation and generate embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert conversation
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
        
        # Generate and store embedding asynchronously
        self._generate_embedding(conversation_id, f"{prompt} {response}")
        
        # Create search index tokens
        self._index_conversation_text(conversation_id, f"{prompt} {response}")
        
        print(f"💾 Stored conversation {conversation_id}")
        return conversation_id
    
    def _generate_embedding(self, conversation_id: int, text: str):
        """Generate embedding using Archie and store it"""
        try:
            response = requests.post(f"{self.base_url}/embeddings",
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5-embedding",
                    "input": text
                })
            
            if response.status_code == 200:
                embedding = response.json()['data'][0]['embedding']
                
                # Store embedding as binary blob
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversation_embeddings (conversation_id, embedding_vector)
                    VALUES (?, ?)
                ''', (conversation_id, pickle.dumps(embedding)))
                conn.commit()
                conn.close()
                
                print(f"🔍 Generated embedding for conversation {conversation_id}")
            
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
    
    def _index_conversation_text(self, conversation_id: int, text: str):
        """Create search index tokens from conversation text"""
        # Simple tokenization (could be enhanced with proper NLP)
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            # Remove punctuation and filter out short words
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 2:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Store in search index
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for word, freq in word_freq.items():
            cursor.execute('''
                INSERT OR REPLACE INTO search_index (conversation_id, token, term_frequency)
                VALUES (?, ?, ?)
            ''', (conversation_id, word, freq))
        
        conn.commit()
        conn.close()
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search conversations by text content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple text search (can be enhanced with TF-IDF scoring)
        search_terms = query.lower().split()
        
        if len(search_terms) == 1:
            cursor.execute('''
                SELECT DISTINCT c.id, c.timestamp, c.session_id, c.prompt, c.response, c.metadata
                FROM conversations c
                JOIN search_index si ON c.id = si.conversation_id
                WHERE si.token LIKE ?
                ORDER BY c.timestamp DESC
                LIMIT ?
            ''', (f'%{search_terms[0]}%', limit))
        else:
            # Multi-term search
            cursor.execute('''
                SELECT c.id, c.timestamp, c.session_id, c.prompt, c.response, c.metadata
                FROM conversations c 
                WHERE c.prompt LIKE ? OR c.response LIKE ?
                ORDER BY c.timestamp DESC
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
        print(f"🔍 Found {len(results)} conversations matching '{query}'")
        return results
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get most recent conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, session_id, prompt, response, metadata
            FROM conversations 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'session_id': row[2],
                'prompt': row[3][:100] + "..." if len(row[3]) > 100 else row[3],
                'response': row[4][:100] + "..." if len(row[4]) > 100 else row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            })
        
        conn.close()
        return results
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM conversation_embeddings')
        total_embeddings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT token) FROM search_index')
        unique_tokens = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'total_embeddings': total_embeddings,
            'unique_tokens': unique_tokens
        }

# Example usage and testing
if __name__ == "__main__":
    chat_manager = ChatHistoryManager()
    
    # Test storing a conversation
    conversation_id = chat_manager.store_conversation(
        prompt="Hello Leo! I'm Claude Code, just arrived in LeoDock.",
        response="Hello Claude! Welcome to LeoDock! Let's build something amazing together.",
        session_id="test_session_1",
        llm_analysis={"analyzed_by": "claude_code", "sentiment": "positive"},
        metadata={"source": "leodock_intro", "priority": "high"}
    )
    
    # Test search
    results = chat_manager.search_conversations("Leo Claude")
    print(f"\n📋 Search results: {len(results)} found")
    for result in results:
        print(f"  - {result['timestamp']}: {result['prompt'][:50]}...")
    
    # Show statistics
    stats = chat_manager.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"  - Total conversations: {stats['total_conversations']}")
    print(f"  - Total embeddings: {stats['total_embeddings']}")
    print(f"  - Unique tokens: {stats['unique_tokens']}")