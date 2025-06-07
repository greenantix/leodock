# 🦁 LeoDock Phase 2 - Claude Code Mission Tasks

## 🎯 **Current Status: Phase 1 Complete! ✅**
- LLM Communication established with Leo & Archie
- Chat history system operational  
- Three-way AI collaboration working
- Leo now has proper personality and team awareness

## 🚨 **Priority Bug Fix: Browser Multiplication Issue**

**Problem**: Browsers opening randomly/multiplying unexpectedly  
**Impact**: Resource waste, user confusion, potential system instability

### Task 1: Debug Browser Multiplication
```bash
# Create browser debug tool
cat > debug_browser_issue.py << 'EOF'
import psutil
import subprocess
import time
import requests

def monitor_browser_processes():
    """Monitor and log browser process creation"""
    print("🔍 Monitoring browser processes...")
    initial_browsers = []
    
    # Get current browser processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'browser' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower() or 'firefox' in proc.info['name'].lower():
                initial_browsers.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    print(f"📊 Initial browser processes: {len(initial_browsers)}")
    
    while True:
        time.sleep(5)
        current_browsers = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'browser' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower() or 'firefox' in proc.info['name'].lower():
                    current_browsers.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if len(current_browsers) > len(initial_browsers):
            print(f"🚨 NEW BROWSER DETECTED! Count: {len(current_browsers)}")
            for browser in current_browsers:
                if browser not in initial_browsers:
                    print(f"   New: {browser['name']} (PID: {browser['pid']})")
                    print(f"   Command: {' '.join(browser['cmdline'][:3])}")
            initial_browsers = current_browsers

if __name__ == "__main__":
    monitor_browser_processes()
EOF

# Run this in background to catch the multiplication
python debug_browser_issue.py &
```

Ask Leo for help analyzing this:
```bash
python talk_to_leo.py "Leo, we have a browser multiplication bug in LeoDock. Browsers are opening randomly. Can you help me analyze potential causes and solutions?" mode="debugging"
```

### Task 2: Fix WebSocket/Flask Connection Issues
```bash
# Check for multiple server instances
ps aux | grep python | grep -E "(pyxtermjs|leodock|flask)"

# Create connection manager to prevent multiple instances
cat > connection_manager.py << 'EOF'
import socket
import os
import signal
import time

class LeoDockConnectionManager:
    def __init__(self):
        self.ports = [5000, 5001]
        self.lock_files = [f"/tmp/leodock_{port}.lock" for port in self.ports]
    
    def check_port_available(self, port):
        """Check if port is already in use"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    
    def create_lock_file(self, port):
        """Create lock file to prevent multiple instances"""
        lock_file = f"/tmp/leodock_{port}.lock"
        if os.path.exists(lock_file):
            print(f"🔒 Port {port} locked by existing process")
            return False
        
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    
    def cleanup_locks(self):
        """Clean up lock files on exit"""
        for lock_file in self.lock_files:
            if os.path.exists(lock_file):
                os.remove(lock_file)
    
    def safe_start_server(self, port, command):
        """Safely start server only if not already running"""
        if not self.check_port_available(port):
            print(f"⚠️ Server already running on port {port}")
            return False
        
        if not self.create_lock_file(port):
            print(f"⚠️ Could not acquire lock for port {port}")
            return False
        
        print(f"✅ Starting server on port {port}")
        return True

if __name__ == "__main__":
    manager = LeoDockConnectionManager()
    
    # Check current status
    for port in [5000, 5001]:
        available = manager.check_port_available(port)
        print(f"Port {port}: {'Available' if available else 'In Use'}")
EOF

python connection_manager.py
```

## 🚀 **Phase 2 Core Tasks**

### Task 3: Enhanced LLM Communication System
Build the Unix-style communication commands we designed:

```bash
# Create advanced LLM communication system
cat > llm_commands.py << 'EOF'
import requests
import json
import time
import threading
from datetime import datetime

class LLMCommands:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.active_sessions = {}
        self.message_queue = []
    
    def llm_talk(self, participants=["leo", "archie"], topic=""):
        """Interactive chat session between LLMs"""
        session_id = f"talk_{int(time.time())}"
        
        print(f"🗣️ Starting LLM Talk Session: {session_id}")
        print(f"👥 Participants: {', '.join(participants)}")
        print(f"📋 Topic: {topic}")
        print("=" * 50)
        
        self.active_sessions[session_id] = {
            'participants': participants,
            'topic': topic,
            'messages': [],
            'start_time': datetime.now()
        }
        
        # Start conversation
        if "leo" in participants:
            leo_prompt = f"Start a collaborative discussion about: {topic}. You're talking with Archie (embedding specialist) and Claude Code."
            response = self._ask_leo(leo_prompt)
            print(f"🦁 Leo: {response}")
            
            self.active_sessions[session_id]['messages'].append({
                'sender': 'leo',
                'message': response,
                'timestamp': datetime.now()
            })
        
        return session_id
    
    def llm_write(self, to_llm, message, priority="normal"):
        """Send one-way message to specific LLM"""
        print(f"📨 Sending message to {to_llm}")
        print(f"💬 Message: {message}")
        print(f"⚡ Priority: {priority}")
        
        if to_llm.lower() == "leo":
            response = self._ask_leo(f"You received this message: {message}")
            print(f"📥 Leo's response: {response}")
            return response
        elif to_llm.lower() == "archie":
            # Archie processes via embeddings
            embedding_result = self._ask_archie(message)
            print(f"📥 Archie processed message (embedding length: {len(embedding_result) if embedding_result else 0})")
            return embedding_result
    
    def llm_wall(self, message, sender="claude_code"):
        """Broadcast message to all LLMs"""
        print(f"📢 BROADCAST from {sender}")
        print(f"🔊 Message: {message}")
        print("=" * 40)
        
        # Send to Leo
        leo_response = self._ask_leo(f"System broadcast: {message}")
        print(f"🦁 Leo acknowledges: {leo_response}")
        
        # Process with Archie
        archie_result = self._ask_archie(f"Broadcast: {message}")
        print(f"🔍 Archie processed broadcast")
        
        return {"leo": leo_response, "archie": "processed"}
    
    def llm_screen(self, session_name, purpose=""):
        """Create shared working session"""
        session_id = f"screen_{session_name}_{int(time.time())}"
        
        print(f"🖥️ Creating shared session: {session_name}")
        print(f"🎯 Purpose: {purpose}")
        
        self.active_sessions[session_id] = {
            'type': 'screen',
            'name': session_name,
            'purpose': purpose,
            'shared_context': {},
            'participants': ['claude_code', 'leo', 'archie'],
            'created': datetime.now()
        }
        
        # Initialize session with Leo
        leo_init = self._ask_leo(f"Starting shared work session '{session_name}' for: {purpose}")
        print(f"🦁 Leo joined session: {leo_init}")
        
        return session_id
    
    def _ask_leo(self, prompt):
        """Helper to communicate with Leo"""
        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                json={
                    "model": "meta-llama-3.1-8b-instruct",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                })
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Leo connection error: {response.status_code}"
        except Exception as e:
            return f"Leo error: {str(e)}"
    
    def _ask_archie(self, text):
        """Helper to get embeddings from Archie"""
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
            return None

# CLI Interface
if __name__ == "__main__":
    import sys
    llm = LLMCommands()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python llm_commands.py talk <topic>")
        print("  python llm_commands.py write <llm> <message>")
        print("  python llm_commands.py wall <message>") 
        print("  python llm_commands.py screen <session_name> <purpose>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "talk" and len(sys.argv) > 2:
        topic = " ".join(sys.argv[2:])
        llm.llm_talk(topic=topic)
    elif command == "write" and len(sys.argv) > 3:
        to_llm = sys.argv[2]
        message = " ".join(sys.argv[3:])
        llm.llm_write(to_llm, message)
    elif command == "wall" and len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
        llm.llm_wall(message)
    elif command == "screen" and len(sys.argv) > 3:
        session_name = sys.argv[2]
        purpose = " ".join(sys.argv[3:])
        llm.llm_screen(session_name, purpose)
EOF

# Test the new commands
python llm_commands.py talk "How to fix browser multiplication bug in LeoDock"
python llm_commands.py write leo "Can you analyze the pyxtermjs startup process for duplicate browser launches?"
python llm_commands.py wall "Starting Phase 2 development - browser bug fix priority"
```

### Task 4: Advanced Chat History with Semantic Search
```bash
# Enhanced chat history with Archie's embeddings
cat > advanced_chat_history.py << 'EOF'
import sqlite3
import json
import requests
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

class AdvancedChatHistory:
    def __init__(self, db_path="data/leodock_conversations.db"):
        self.db_path = db_path
        self.base_url = "http://127.0.0.1:1234/v1"
        self.init_database()
    
    def init_database(self):
        """Enhanced database with embeddings"""
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
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, participant, message, session_id=None, metadata=None):
        """Save conversation with embedding"""
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
        
        print(f"💾 Saved conversation: {participant} → {message[:50]}...")
        return conversation_id
    
    def semantic_search(self, query, limit=10, similarity_threshold=0.7):
        """Search conversations using semantic similarity"""
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            print("❌ Could not generate embedding for query")
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, participant, message, embedding_vector, timestamp
            FROM conversations 
            WHERE embedding_vector IS NOT NULL
        ''')
        
        results = []
        for row in cursor.fetchall():
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
                    'similarity': similarity
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        conn.close()
        
        return results[:limit]
    
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
            print(f"Archie embedding error: {e}")
            return None

# CLI Interface
if __name__ == "__main__":
    import sys
    history = AdvancedChatHistory()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python advanced_chat_history.py save <participant> <message>")
        print("  python advanced_chat_history.py search <query>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "save" and len(sys.argv) > 3:
        participant = sys.argv[2]
        message = " ".join(sys.argv[3:])
        history.save_conversation(participant, message)
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = history.semantic_search(query)
        
        print(f"🔍 Semantic search results for: '{query}'")
        print("=" * 50)
        for result in results:
            print(f"📝 {result['participant']}: {result['message'][:100]}...")
            print(f"   Similarity: {result['similarity']:.3f} | {result['timestamp']}")
            print()
EOF

# Test semantic search
python advanced_chat_history.py save claude_code "Working on browser multiplication bug fix"
python advanced_chat_history.py save leo "Analyzing browser startup processes for duplicates"
python advanced_chat_history.py search "browser bug"
```

### Task 5: Real-time Platform Monitoring
```bash
# Platform health monitor
cat > leodock_monitor.py << 'EOF'
import psutil
import requests
import time
import subprocess
from datetime import datetime

class LeoDockMonitor:
    def __init__(self):
        self.services = {
            'terminal': 'http://127.0.0.1:5000',
            'dashboard': 'http://127.0.0.1:5001', 
            'lm_studio': 'http://127.0.0.1:1234/v1/models'
        }
    
    def check_service_health(self):
        """Check health of all LeoDock services"""
        print(f"🏥 LeoDock Health Check - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        for service, url in self.services.items():
            try:
                response = requests.get(url, timeout=5)
                status = "✅ Healthy" if response.status_code == 200 else f"⚠️ Status {response.status_code}"
            except requests.exceptions.RequestException as e:
                status = f"❌ Down ({str(e)[:30]}...)"
            
            print(f"{service.capitalize()}: {status}")
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        print(f"\n🖥️ System Resources:")
        print(f"CPU Usage: {cpu_percent}%")
        print(f"Memory: {memory.percent}% ({memory.used // 1024**2}MB / {memory.total // 1024**2}MB)")
        
        # Check for multiple browser processes
        browser_count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if any(browser in proc.info['name'].lower() 
                      for browser in ['chrome', 'firefox', 'browser']):
                    browser_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"Browser Processes: {browser_count} {'⚠️' if browser_count > 3 else '✅'}")
        
        return {
            'services': self.services,
            'cpu': cpu_percent,
            'memory': memory.percent,
            'browsers': browser_count
        }
    
    def auto_fix_issues(self):
        """Automatically fix common issues"""
        print("\n🔧 Auto-fixing common issues...")
        
        # Kill excessive browser processes
        browser_pids = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower() and 'leodock' not in ' '.join(proc.info['cmdline']):
                    browser_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if len(browser_pids) > 2:
            print(f"🗑️ Killing {len(browser_pids) - 2} excess browser processes")
            for pid in browser_pids[2:]:  # Keep first 2
                try:
                    psutil.Process(pid).terminate()
                except psutil.NoSuchProcess:
                    pass

if __name__ == "__main__":
    monitor = LeoDockMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Continuous monitoring
        while True:
            monitor.check_service_health()
            monitor.auto_fix_issues()
            print("\n" + "="*50 + "\n")
            time.sleep(30)
    else:
        # Single check
        monitor.check_service_health()
        monitor.auto_fix_issues()
EOF

# Start monitoring
python leodock_monitor.py watch &
```

## 📋 **Task Summary for Claude Code:**

### 🚨 **Immediate (Fix Browser Bug):**
1. Run browser debug monitor
2. Ask Leo to analyze the issue
3. Implement connection manager
4. Test browser multiplication fix

### 🚀 **Core Development:**
1. Implement Unix-style LLM commands (talk/write/wall/screen)
2. Build advanced semantic search with Archie
3. Create platform health monitoring
4. Enhance real-time collaboration

### 🎯 **Advanced Features:**
1. Code analysis pipelines
2. Collaborative debugging sessions
3. Intelligent project management
4. Self-modifying platform capabilities

## 🔥 **Test Commands:**

```bash
# Debug browser issue
python debug_browser_issue.py &
python talk_to_leo.py "Help me fix browser multiplication" mode="debugging"

# Test new LLM commands
python llm_commands.py talk "Phase 2 development strategy"
python llm_commands.py wall "Browser bug investigation in progress"

# Monitor platform health
python leodock_monitor.py
```

**Ready to tackle Phase 2, Claude Code! Let's fix that browser bug and build advanced features!** 🦁🚀