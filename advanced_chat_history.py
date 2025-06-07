import sqlite3
import json
import requests
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

class AdvancedChatHistory:
    def __init__(self, db_path="data/leodock_conversations.db"):
        self.db_path = db_path
        self.base_url = "http://127.0.0.1:1234/v1"
        self.init_database()
    
    def init_database(self):
        """Enhanced database with embeddings"""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                participant TEXT,
                message TEXT NOT NULL,
                embedding_vector TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                session_type TEXT,
                participants TEXT,
                topic TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participant ON conversations(participant)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON conversations(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)')
        
        conn.commit()
        conn.close()
        print("📊 Advanced chat history database initialized!")
    
    def save_conversation(self, participant, message, session_id=None, metadata=None):
        """Save conversation with embedding"""
        print(f"💾 Saving conversation from {participant}...")
        
        # Get embedding from Archie
        embedding = self._get_embedding(message)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, session_id, participant, message, embedding_vector, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            session_id,
            participant,
            message,
            json.dumps(embedding) if embedding else None,
            json.dumps(metadata) if metadata else None
        ))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Saved conversation {conversation_id}: {participant} → {message[:50]}...")
        return conversation_id
    
    def save_session(self, session_id, session_type, participants, topic, status='active'):
        """Save LLM session metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO llm_sessions 
            (session_id, session_type, participants, topic, start_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_type,
            json.dumps(participants) if isinstance(participants, list) else participants,
            topic,
            datetime.now().isoformat(),
            status
        ))
        
        conn.commit()
        conn.close()
        print(f"📋 Saved session: {session_id} ({session_type})")
    
    def semantic_search(self, query, limit=10, similarity_threshold=0.6):
        """Search conversations using semantic similarity"""
        print(f"🔍 Performing semantic search for: '{query}'")
        
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            print("❌ Could not generate embedding for query")
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, participant, message, embedding_vector, timestamp, session_id
            FROM conversations 
            WHERE embedding_vector IS NOT NULL
        ''')
        
        results = []
        for row in cursor.fetchall():
            try:
                stored_embedding = json.loads(row[3])
                
                # Calculate similarity
                similarity = cosine_similarity(
                    [query_embedding], 
                    [stored_embedding]
                )[0][0]
                
                if similarity >= similarity_threshold:
                    results.append({
                        'id': row[0],
                        'participant': row[1],
                        'message': row[2],
                        'timestamp': row[4],
                        'session_id': row[5],
                        'similarity': similarity
                    })
            except (json.JSONDecodeError, IndexError):
                continue
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        conn.close()
        
        print(f"🎯 Found {len(results)} semantically similar conversations")
        return results[:limit]
    
    def text_search(self, query, limit=20):
        """Traditional text-based search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, participant, message, timestamp, session_id
            FROM conversations 
            WHERE message LIKE ? OR participant LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'participant': row[1],
                'message': row[2],
                'timestamp': row[3],
                'session_id': row[4],
                'similarity': 1.0  # Text matches get max similarity
            })
        
        conn.close()
        return results
    
    def get_conversation_context(self, conversation_id, context_size=3):
        """Get conversation context around a specific message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the target conversation
        cursor.execute('SELECT session_id, timestamp FROM conversations WHERE id = ?', (conversation_id,))
        result = cursor.fetchone()
        
        if not result:
            return []
        
        session_id, timestamp = result
        
        # Get conversations from same session around the timestamp
        cursor.execute('''
            SELECT id, participant, message, timestamp
            FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp
        ''', (session_id,))
        
        all_messages = cursor.fetchall()
        
        # Find the target message index
        target_index = -1
        for i, msg in enumerate(all_messages):
            if msg[0] == conversation_id:
                target_index = i
                break
        
        if target_index == -1:
            return []
        
        # Get context around the target
        start_idx = max(0, target_index - context_size)
        end_idx = min(len(all_messages), target_index + context_size + 1)
        
        context = []
        for i in range(start_idx, end_idx):
            msg = all_messages[i]
            context.append({
                'id': msg[0],
                'participant': msg[1],
                'message': msg[2],
                'timestamp': msg[3],
                'is_target': i == target_index
            })
        
        conn.close()
        return context
    
    def get_session_statistics(self):
        """Get statistics about conversations and sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total conversations
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Conversations with embeddings
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE embedding_vector IS NOT NULL')
        conversations_with_embeddings = cursor.fetchone()[0]
        
        # Unique participants
        cursor.execute('SELECT COUNT(DISTINCT participant) FROM conversations')
        unique_participants = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute('SELECT COUNT(*) FROM llm_sessions WHERE status = "active"')
        active_sessions = cursor.fetchone()[0]
        
        # Most active participant
        cursor.execute('''
            SELECT participant, COUNT(*) as msg_count 
            FROM conversations 
            GROUP BY participant 
            ORDER BY msg_count DESC 
            LIMIT 1
        ''')
        most_active = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'conversations_with_embeddings': conversations_with_embeddings,
            'unique_participants': unique_participants,
            'active_sessions': active_sessions,
            'most_active_participant': most_active[0] if most_active else None,
            'most_active_count': most_active[1] if most_active else 0
        }
    
    def _get_embedding(self, text):
        """Get embedding from Archie"""
        try:
            response = requests.post(f"{self.base_url}/embeddings",
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5-embedding",
                    "input": text
                })
            
            if response.status_code == 200:
                return response.json()['data'][0]['embedding']
            return None
        except Exception as e:
            print(f"❌ Archie embedding error: {e}")
            return None

# CLI Interface
def main():
    history = AdvancedChatHistory()
    
    if len(sys.argv) < 2:
        print("🗣️ Advanced Chat History - LeoDock Platform")
        print("=" * 50)
        print("Usage:")
        print("  python advanced_chat_history.py save <participant> <message>")
        print("  python advanced_chat_history.py search <query>")
        print("  python advanced_chat_history.py semantic <query>")
        print("  python advanced_chat_history.py context <conversation_id>")
        print("  python advanced_chat_history.py stats")
        print("  python advanced_chat_history.py demo")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "save" and len(sys.argv) > 3:
        participant = sys.argv[2]
        message = " ".join(sys.argv[3:])
        conversation_id = history.save_conversation(participant, message)
        print(f"💾 Conversation saved with ID: {conversation_id}")
        
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = history.text_search(query)
        
        print(f"🔍 Text search results for: '{query}'")
        print("=" * 50)
        for result in results:
            print(f"📝 {result['participant']}: {result['message'][:80]}...")
            print(f"   ID: {result['id']} | {result['timestamp']}")
            print()
            
    elif command == "semantic" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = history.semantic_search(query)
        
        print(f"🧠 Semantic search results for: '{query}'")
        print("=" * 50)
        for result in results:
            print(f"📝 {result['participant']}: {result['message'][:80]}...")
            print(f"   Similarity: {result['similarity']:.3f} | {result['timestamp']}")
            print()
            
    elif command == "context" and len(sys.argv) > 2:
        try:
            conversation_id = int(sys.argv[2])
            context = history.get_conversation_context(conversation_id)
            
            print(f"📄 Conversation context for ID {conversation_id}")
            print("=" * 50)
            for msg in context:
                marker = "🎯" if msg['is_target'] else "  "
                print(f"{marker} {msg['participant']}: {msg['message'][:60]}...")
                print(f"    {msg['timestamp']}")
                print()
        except ValueError:
            print("❌ Invalid conversation ID")
            
    elif command == "stats":
        stats = history.get_session_statistics()
        print("📊 Advanced Chat History Statistics")
        print("=" * 40)
        print(f"Total conversations: {stats['total_conversations']}")
        print(f"With embeddings: {stats['conversations_with_embeddings']}")
        print(f"Unique participants: {stats['unique_participants']}")
        print(f"Active sessions: {stats['active_sessions']}")
        if stats['most_active_participant']:
            print(f"Most active: {stats['most_active_participant']} ({stats['most_active_count']} messages)")
            
    elif command == "demo":
        print("🚀 Running Advanced Chat History Demo")
        print("=" * 40)
        
        # Save some demo conversations
        session_id = f"demo_{int(datetime.now().timestamp())}"
        
        demo_conversations = [
            ("claude_code", "Starting Phase 2 development with browser bug fixes"),
            ("leo", "I'll help analyze the browser multiplication issue"),
            ("archie", "Generated embeddings for semantic analysis"),
            ("claude_code", "Implementing connection manager to prevent duplicate processes")
        ]
        
        for participant, message in demo_conversations:
            history.save_conversation(participant, message, session_id)
        
        # Test searches
        print(f"\n🔍 Testing semantic search for 'browser issues':")
        results = history.semantic_search("browser issues", limit=3)
        for result in results:
            print(f"  - {result['participant']}: {result['message'][:50]}... (similarity: {result['similarity']:.3f})")
        
        # Show stats
        print(f"\n📊 Demo Statistics:")
        stats = history.get_session_statistics()
        print(f"  Total conversations: {stats['total_conversations']}")
        print(f"  With embeddings: {stats['conversations_with_embeddings']}")
        
        print(f"\n✅ Demo complete!")
    else:
        print("❌ Unknown command or missing arguments")

if __name__ == "__main__":
    main()