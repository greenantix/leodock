# LeoDock Enhanced Platform - Build Instructions

## 🎯 **Current Status: ✅ WORKING**
- Real terminal working in browser
- Claude Code running inside terminal  
- Perfect foundation established

## 🚀 **Next: Build the Enhanced Platform**

I'll help you extend LeoDock with the full Claude Code integration platform. Here's what we'll add:

## 📁 **New Project Structure**

```
leodock/
├── pyxtermjs/              # Original terminal (keep as-is)
├── extensions/             # NEW: Platform extensions
│   ├── __init__.py
│   ├── llm_manager.py     # LM Studio dual LLM system
│   ├── chat_history.py    # Conversation storage & search
│   ├── communication.py   # LLM-to-LLM talk/write/wall
│   ├── claude_session.py  # Enhanced Claude Code management
│   └── ui_manager.py      # Multi-panel interface
├── static/                 # NEW: Enhanced UI
│   ├── css/
│   │   └── leodock.css    # Custom styling
│   └── js/
│       ├── llm-panel.js   # LLM interaction panel
│       ├── chat-history.js # History search & display
│       └── communication.js # LLM communication UI
├── templates/              # NEW: Enhanced interface
│   ├── dashboard.html     # Multi-panel main interface
│   ├── components/        # Reusable UI components
│   └── layouts/           # Base layouts
├── config/                 # NEW: Configuration
│   ├── settings.py        # App configuration
│   ├── database.py        # SQLite setup
│   └── lm_studio.py       # LM Studio connection config
├── data/                   # NEW: Data storage
│   ├── conversations.db   # SQLite database
│   └── logs/              # Application logs
├── requirements-enhanced.txt # Extended dependencies
└── run_leodock.py         # Main startup script
```

## 🛠️ **Phase 1: Enhanced UI (Multi-Panel Interface)**

First, let's create a dashboard that shows:
- **Left Panel:** Your working terminal (current pyxtermjs)
- **Right Panel:** LLM interaction area
- **Bottom Panel:** Chat history with search
- **Top Panel:** System status and controls

### **File: templates/dashboard.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeoDock - Claude Code Integration Platform</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/leodock.css') }}">
</head>
<body>
    <div class="leodock-container">
        <!-- Top Status Bar -->
        <div class="status-bar">
            <div class="status-left">
                <h1>🦁 LeoDock</h1>
                <span class="status-indicator">● Terminal: Active</span>
                <span class="status-indicator">● LLMs: {{ llm_status }}</span>
            </div>
            <div class="status-right">
                <button id="start-collaboration">Start LLM Collaboration</button>
                <button id="view-logs">View Logs</button>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="main-content">
            <!-- Left: Terminal Panel -->
            <div class="panel terminal-panel">
                <div class="panel-header">
                    <h3>Claude Code Terminal</h3>
                    <div class="terminal-controls">
                        <button onclick="restartTerminal()">Restart</button>
                        <button onclick="clearTerminal()">Clear</button>
                    </div>
                </div>
                <div class="panel-content">
                    <!-- Embed the working terminal -->
                    <iframe src="http://localhost:5000" class="terminal-frame"></iframe>
                </div>
            </div>

            <!-- Right: LLM Interaction Panel -->
            <div class="panel llm-panel">
                <div class="panel-header">
                    <h3>LLM Assistance</h3>
                    <select id="llm-selector">
                        <option value="indexing">IndexingLLM (Leo)</option>
                        <option value="quality">QualityLLM (Quinn)</option>
                        <option value="fallback">Fallback API</option>
                    </select>
                </div>
                <div class="panel-content">
                    <div class="llm-output" id="llm-output"></div>
                    <div class="llm-input-area">
                        <textarea id="llm-prompt" placeholder="Ask the LLMs for help..."></textarea>
                        <button onclick="sendToLLM()">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom: Chat History Panel -->
        <div class="panel history-panel">
            <div class="panel-header">
                <h3>Conversation History</h3>
                <div class="history-controls">
                    <input type="text" id="search-input" placeholder="Search conversations...">
                    <button onclick="searchHistory()">Search</button>
                    <button onclick="exportHistory()">Export</button>
                </div>
            </div>
            <div class="panel-content">
                <div class="history-list" id="history-list">
                    <!-- Chat history will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/leodock.js') }}"></script>
</body>
</html>
```

## 🔧 **Phase 2: LLM Integration System**

### **File: extensions/llm_manager.py**
```python
import requests
import sqlite3
import asyncio
from datetime import datetime
import json

class LLMManager:
    def __init__(self):
        self.lm_studio_url = "http://localhost:1234/v1"
        self.models = {
            'indexing': 'your-indexing-model-name',
            'quality': 'your-qa-model-name'
        }
        self.fallback_api_key = None  # Set from config
        self.conversations = []
        
    async def send_to_indexing_llm(self, prompt, context=""):
        """Send prompt to IndexingLLM for embedding/search tasks"""
        try:
            response = requests.post(f"{self.lm_studio_url}/chat/completions", 
                json={
                    "model": self.models['indexing'],
                    "messages": [
                        {"role": "system", "content": "You are IndexingLLM. You specialize in code analysis, embedding generation, and knowledge management."},
                        {"role": "user", "content": f"Context: {context}\n\nTask: {prompt}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                })
            return response.json()
        except Exception as e:
            return {"error": f"IndexingLLM error: {str(e)}"}
    
    async def send_to_quality_llm(self, prompt, context=""):
        """Send prompt to QualityLLM for analysis and QA"""
        try:
            response = requests.post(f"{self.lm_studio_url}/chat/completions", 
                json={
                    "model": self.models['quality'],
                    "messages": [
                        {"role": "system", "content": "You are QualityLLM. You analyze code quality, detect drift, and ensure consistency."},
                        {"role": "user", "content": f"Context: {context}\n\nAnalyze: {prompt}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                })
            return response.json()
        except Exception as e:
            return {"error": f"QualityLLM error: {str(e)}"}
    
    async def analyze_claude_conversation(self, conversation_text):
        """Analyze a Claude Code conversation with both LLMs"""
        # Send to IndexingLLM for embedding and indexing
        indexing_task = self.send_to_indexing_llm(
            "Generate embeddings and index this conversation", 
            conversation_text
        )
        
        # Send to QualityLLM for drift detection
        quality_task = self.send_to_quality_llm(
            "Analyze this conversation for quality, consistency, and potential drift",
            conversation_text
        )
        
        # Run both in parallel
        indexing_result, quality_result = await asyncio.gather(indexing_task, quality_task)
        
        return {
            'indexing': indexing_result,
            'quality': quality_result,
            'timestamp': datetime.now().isoformat()
        }
```

## 🗃️ **Phase 3: Chat History & Search**

### **File: extensions/chat_history.py**
```python
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
```

## 🚀 **Main Startup Script**

### **File: run_leodock.py**
```python
#!/usr/bin/env python3
"""
LeoDock - Claude Code Integration Platform
Main startup script that runs the enhanced platform
"""

import subprocess
import threading
import time
import webbrowser
from flask import Flask, render_template, jsonify, request
from extensions.llm_manager import LLMManager
from extensions.chat_history import ChatHistoryManager

app = Flask(__name__)
llm_manager = LLMManager()
chat_manager = ChatHistoryManager()

# Global to track terminal process
terminal_process = None

def start_terminal_server():
    """Start the pyxtermjs terminal server"""
    global terminal_process
    terminal_process = subprocess.Popen([
        'python', '-m', 'pyxtermjs', 
        '--command', 'bash',
        '--port', '5000'
    ])

@app.route('/')
def dashboard():
    """Main dashboard with multi-panel interface"""
    return render_template('dashboard.html', llm_status="Connected")

@app.route('/api/llm/send', methods=['POST'])
async def send_to_llm():
    """API endpoint to send prompts to LLMs"""
    data = request.json
    llm_type = data.get('llm_type', 'indexing')
    prompt = data.get('prompt', '')
    context = data.get('context', '')
    
    if llm_type == 'indexing':
        result = await llm_manager.send_to_indexing_llm(prompt, context)
    elif llm_type == 'quality':
        result = await llm_manager.send_to_quality_llm(prompt, context)
    else:
        result = {"error": "Unknown LLM type"}
    
    return jsonify(result)

@app.route('/api/history/search')
def search_history():
    """API endpoint to search conversation history"""
    query = request.args.get('q', '')
    results = chat_manager.search_conversations(query)
    return jsonify(results)

if __name__ == '__main__':
    print("🦁 Starting LeoDock Platform...")
    
    # Start terminal server in background
    print("📺 Starting terminal server...")
    terminal_thread = threading.Thread(target=start_terminal_server, daemon=True)
    terminal_thread.start()
    
    # Wait for terminal to start
    time.sleep(3)
    
    # Start main dashboard
    print("🚀 Starting dashboard on http://localhost:5001")
    print("📺 Terminal available on http://localhost:5000")
    
    # Open browser automatically
    webbrowser.open('http://localhost:5001')
    
    # Run dashboard server
    app.run(host='0.0.0.0', port=5001, debug=True)
```

## 📋 **Installation & Usage**

### **Create the enhanced platform:**
```bash
cd leodock

# Create new directories
mkdir -p extensions static/css static/js templates config data

# Install additional dependencies
pip install flask requests sqlite3

# Create the files above in their respective locations

# Run the enhanced platform
python run_leodock.py
```

This will open:
- **Main Dashboard:** http://localhost:5001 (multi-panel interface)
- **Terminal:** http://localhost:5000 (your working Claude Code terminal)

## 🎯 **What You Get:**

1. **Multi-Panel Interface** - Terminal + LLM panels + history
2. **Dual LLM System** - IndexingLLM and QualityLLM working together  
3. **Chat History** - Store and search all Claude Code conversations
4. **Real Terminal** - Your working Claude Code terminal embedded
5. **LLM Communication** - APIs ready for the talk/write/wall system

Ready to build this enhanced platform? 🚀