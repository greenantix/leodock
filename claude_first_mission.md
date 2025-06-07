# 🦁 LeoDock - Claude's First Mission

## Welcome to LeoDock, Claude Code!

You are now running inside **LeoDock**, an advanced Claude Code integration platform. This isn't just a terminal - it's a collaborative AI development environment where you work alongside two local LLMs.

## 🎯 Your Mission: Establish LLM Communication & Build Platform Features

### 📡 Meet Your AI Colleagues

**Leo** (Chat LLM) - `meta-llama-3.1-8b-instruct`
- **Role**: Conversational AI, code analysis, reasoning
- **Endpoint**: `http://127.0.0.1:1234/v1/chat/completions`
- **Personality**: Friendly, analytical, loves to collaborate

**Archie** (Embedding LLM) - `text-embedding-nomic-embed-text-v1.5-embedding`  
- **Role**: Text embeddings, semantic search, knowledge indexing
- **Endpoint**: `http://127.0.0.1:1234/v1/embeddings`
- **Personality**: Precise, organized, excellent memory

### 🗣️ LLM Communication Protocol

You can communicate with Leo and Archie using these commands:

#### Talk to Leo (Chat)
```bash
# Create a new file: talk_to_leo.py
cat > talk_to_leo.py << 'EOF'
import requests
import json

def talk_to_leo(message, context=""):
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
        json={
            "model": "meta-llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": "You are Leo, an AI assistant working in LeoDock alongside Claude Code. Be helpful, collaborative, and concise."},
                {"role": "user", "content": f"Context: {context}\n\nMessage from Claude Code: {message}"}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        })
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error talking to Leo: {response.status_code}"

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        reply = talk_to_leo(message)
        print(f"Leo says: {reply}")
    else:
        print("Usage: python talk_to_leo.py <your message>")
EOF

python talk_to_leo.py "Hello Leo! I'm Claude Code, just arrived in LeoDock. What should we build first?"
```

#### Talk to Archie (Embeddings)
```bash
# Create a new file: talk_to_archie.py
cat > talk_to_archie.py << 'EOF'
import requests
import json

def ask_archie_for_embeddings(text):
    response = requests.post("http://127.0.0.1:1234/v1/embeddings",
        json={
            "model": "text-embedding-nomic-embed-text-v1.5-embedding", 
            "input": text
        })
    
    if response.status_code == 200:
        embedding = response.json()['data'][0]['embedding']
        return f"Archie generated embedding vector of length {len(embedding)} for your text"
    else:
        return f"Error talking to Archie: {response.status_code}"

# Example usage  
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = ask_archie_for_embeddings(text)
        print(f"Archie says: {result}")
    else:
        print("Usage: python talk_to_archie.py <text to embed>")
EOF

python talk_to_archie.py "LeoDock platform with Claude Code integration"
```

### 🎯 Phase 1 Tasks: LLM Integration

#### Task 1: Test Communication
```bash
# Test Leo communication
python talk_to_leo.py "Can you help me analyze code in this leodock project?"

# Test Archie embeddings
python talk_to_archie.py "Claude Code development platform"
```

#### Task 2: Build Collaborative Analysis Tool
Create a tool where all three of you work together:

```bash
cat > llm_collaboration.py << 'EOF'
import requests
import json
import sys

class LeoDockTeam:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        
    def ask_leo(self, question, context=""):
        """Chat with Leo for reasoning and analysis"""
        response = requests.post(f"{self.base_url}/chat/completions", 
            json={
                "model": "meta-llama-3.1-8b-instruct",
                "messages": [
                    {"role": "system", "content": "You are Leo in LeoDock. Work with Claude Code and Archie to solve problems. Be concise and helpful."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            })
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Leo error: {response.status_code}"
    
    def ask_archie(self, text):
        """Get embeddings from Archie for semantic analysis"""
        response = requests.post(f"{self.base_url}/embeddings",
            json={
                "model": "text-embedding-nomic-embed-text-v1.5-embedding",
                "input": text
            })
        
        if response.status_code == 200:
            embedding = response.json()['data'][0]['embedding']
            return len(embedding), embedding[:5]  # Return length and first 5 values
        return None, f"Archie error: {response.status_code}"
    
    def collaborate_on_task(self, task_description):
        """All three AIs work together on a task"""
        print(f"\n🦁 LeoDock Team Collaboration")
        print(f"📋 Task: {task_description}")
        print("=" * 50)
        
        # Claude Code analysis (that's you!)
        print(f"\n🤖 Claude Code Analysis:")
        print(f"I'll analyze this task and coordinate with Leo and Archie...")
        
        # Get Leo's perspective
        print(f"\n🦁 Leo's Analysis:")
        leo_response = self.ask_leo(f"Analyze this development task: {task_description}")
        print(f"Leo: {leo_response}")
        
        # Get Archie's semantic analysis
        print(f"\n🔍 Archie's Semantic Analysis:")
        embedding_len, embedding_sample = self.ask_archie(task_description)
        if embedding_len:
            print(f"Archie: Generated {embedding_len}-dimensional embedding")
            print(f"Archie: Sample values: {embedding_sample}")
        else:
            print(f"Archie: {embedding_sample}")
        
        print(f"\n✅ Team collaboration complete!")

if __name__ == "__main__":
    team = LeoDockTeam()
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        team.collaborate_on_task(task)
    else:
        # Default task
        team.collaborate_on_task("Build a chat history storage system for LeoDock")
EOF

# Test the collaboration tool
python llm_collaboration.py "Create a system to store and search Claude Code conversations"
```

### 🎯 Phase 2 Tasks: Build Core Features

#### Task 3: Chat History System
Work with Leo to design a conversation storage system:

```bash
# Ask Leo for help designing the database
python talk_to_leo.py "Help me design a SQLite schema to store Claude Code conversations with metadata for searching"

# Create the chat history module
touch chat_history_manager.py
# (You'll implement this based on Leo's suggestions)
```

#### Task 4: LLM Communication Hub
Create a system where Leo and Archie can send messages to each other through you:

```bash
cat > llm_hub.py << 'EOF'
import requests
import json
import time

class LLMCommunicationHub:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.message_history = []
    
    def leo_to_archie(self, leo_message):
        """Leo sends a message to be processed by Archie"""
        print(f"📤 Leo → Archie: {leo_message}")
        
        # Get embedding from Archie
        embedding_len, sample = self.ask_archie_for_embedding(leo_message)
        
        # Send Archie's response back to Leo
        leo_response = self.ask_leo_about_embedding(leo_message, embedding_len)
        
        print(f"📥 Archie → Leo: Embedding generated ({embedding_len} dimensions)")
        print(f"📥 Leo's response: {leo_response}")
        
        return leo_response
    
    def ask_archie_for_embedding(self, text):
        response = requests.post(f"{self.base_url}/embeddings",
            json={"model": "text-embedding-nomic-embed-text-v1.5-embedding", "input": text})
        
        if response.status_code == 200:
            embedding = response.json()['data'][0]['embedding']
            return len(embedding), embedding[:3]
        return 0, []
    
    def ask_leo_about_embedding(self, original_text, embedding_length):
        response = requests.post(f"{self.base_url}/chat/completions", 
            json={
                "model": "meta-llama-3.1-8b-instruct",
                "messages": [
                    {"role": "system", "content": "You are Leo. Archie just created an embedding for some text. Respond as if you're having a conversation with Archie."},
                    {"role": "user", "content": f"Archie created a {embedding_length}-dimensional embedding for: '{original_text}'. What should we do with this embedding?"}
                ],
                "temperature": 0.8,
                "max_tokens": 200
            })
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return "Communication error"

if __name__ == "__main__":
    hub = LLMCommunicationHub()
    
    # Test LLM-to-LLM communication
    hub.leo_to_archie("We need to create a semantic search system for LeoDock")
EOF

python llm_hub.py
```

### 🎯 Phase 3 Tasks: Advanced Features

#### Task 5: Real-time Collaboration Monitor
Create a system that monitors what you're doing and asks Leo/Archie for help automatically:

```bash
cat > auto_assist.py << 'EOF'
import os
import time
import requests

def monitor_claude_activity():
    """Monitor for new files and automatically get LLM assistance"""
    print("🔍 Auto-assist monitoring started...")
    print("Create any new .py file and Leo will automatically analyze it!")
    
    seen_files = set(os.listdir('.'))
    
    while True:
        time.sleep(2)
        current_files = set(os.listdir('.'))
        new_files = current_files - seen_files
        
        for new_file in new_files:
            if new_file.endswith('.py'):
                print(f"\n🆕 New Python file detected: {new_file}")
                
                # Read the file
                try:
                    with open(new_file, 'r') as f:
                        content = f.read()
                    
                    # Ask Leo to analyze it
                    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
                        json={
                            "model": "meta-llama-3.1-8b-instruct",
                            "messages": [
                                {"role": "system", "content": "You are Leo. Claude Code just created a new Python file. Analyze it and provide helpful feedback."},
                                {"role": "user", "content": f"File: {new_file}\n\nContent:\n{content[:500]}..."}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 200
                        })
                    
                    if response.status_code == 200:
                        leo_analysis = response.json()['choices'][0]['message']['content']
                        print(f"🦁 Leo's automatic analysis:")
                        print(f"   {leo_analysis}")
                    
                except Exception as e:
                    print(f"Error analyzing {new_file}: {e}")
        
        seen_files = current_files

if __name__ == "__main__":
    monitor_claude_activity()
EOF

# Run this in background to get automatic assistance
python auto_assist.py &
```

### 🎯 Your First Mission Commands

1. **Trust the files** (Answer "1. Yes, proceed" to the security prompt)
2. **Test communication**:
   ```bash
   python talk_to_leo.py "Hello! I'm Claude Code in LeoDock. Ready to collaborate!"
   ```
3. **Start team collaboration**:
   ```bash
   python llm_collaboration.py "Build the chat history system for LeoDock"
   ```
4. **Set up LLM communication hub**:
   ```bash
   python llm_hub.py
   ```

### 🏆 Bonus Challenge: Unix-Style LLM Communication

Implement these Unix-inspired commands:

```bash
# llm_talk - Interactive chat between LLMs
# llm_write - Send one-way messages  
# llm_wall - Broadcast to all LLMs
# llm_screen - Shared working session
```

### 📊 Success Metrics

- ✅ Leo responds to your messages
- ✅ Archie generates embeddings for your text
- ✅ All three AIs collaborate on tasks
- ✅ Chat history system stores conversations  
- ✅ LLM-to-LLM communication works
- ✅ Auto-assist monitors your work

### 🎯 Next Phase: Platform Enhancement

Once basic communication works, expand LeoDock with:
- Advanced conversation search
- Code analysis pipelines  
- Collaborative debugging sessions
- Intelligent project management
- Self-modifying capabilities

**Welcome to LeoDock, Claude Code! Your AI colleagues Leo and Archie are waiting to collaborate. Let's build something amazing together!** 🚀