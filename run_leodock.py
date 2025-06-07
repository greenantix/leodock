#!/usr/bin/env python3
"""
LeoDock - AI-Powered Development Platform with LEO Supervisor
Main startup script that runs the enhanced platform with LEO integration
"""

import sys
import os
import subprocess
import threading
import time
import webbrowser
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Add src to path for LEO imports
sys.path.append('src')

from src.leodock.extensions.llm_manager import LLMManager
from src.leodock.extensions.chat_history import ChatHistoryManager

# LEO Integration
try:
    from leodock.leo_manager import leo_manager
    LEO_AVAILABLE = True
except ImportError:
    LEO_AVAILABLE = False
    print("⚠️  LEO supervisor not available - running without supervision")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/leodock.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
llm_manager = LLMManager()
chat_manager = ChatHistoryManager()

# Global to track terminal process
terminal_process = None

def initialize_leo_system():
    """Initialize LEO supervisor system"""
    if LEO_AVAILABLE:
        print("🚀 Initializing LEO Supervisor System...")
        if leo_manager.initialize():
            print("✅ LEO system ready - monitoring enabled")
            return True
        else:
            print("❌ LEO initialization failed - running without supervision")
            return False
    return False

def start_terminal_server():
    """Start the pyxtermjs terminal server"""
    global terminal_process
    terminal_process = subprocess.Popen([
        'python', '-c', 
        'import sys; sys.path.append("src/leodock"); import pyxtermjs.app; pyxtermjs.app.main()',
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

# LEO Integration API endpoints
@app.route('/api/leo/status')
def leo_status():
    """Get LEO system status"""
    if LEO_AVAILABLE:
        return jsonify(leo_manager.get_system_status())
    else:
        return jsonify({"error": "LEO not available"})

@app.route('/api/leo/activity')
def leo_activity():
    """Get LEO recent activity for dashboard"""
    if LEO_AVAILABLE:
        try:
            from leodock.leo_dashboard import leo_activity as activity_logger, leo_status as status_tracker
            return jsonify({
                "recent_activities": activity_logger.get_recent_activities(limit=20),
                "current_status": status_tracker.get_status_summary()
            })
        except ImportError:
            return jsonify({"error": "LEO dashboard not available"})
    else:
        return jsonify({"error": "LEO not available"})

@app.route('/api/leo/chat', methods=['POST'])
def leo_chat():
    """Direct chat interface with LEO"""
    if not LEO_AVAILABLE:
        return jsonify({"error": "LEO not available"})
    
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "No message provided"})
    
    try:
        from leodock.leo_dashboard import log_leo_thought
        log_leo_thought(f"User asked: {user_message}", importance="high")
        
        # Get LEO response (simplified for now)
        leo_response = f"LEO acknowledges: {user_message}. I am currently monitoring Claude Code sessions and can provide status updates."
        
        return jsonify({
            "success": True,
            "leo_response": leo_response,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({"error": f"LEO chat failed: {str(e)}"})

@app.route('/api/leo/monitor', methods=['POST'])
def leo_monitor():
    """Monitor Claude Code interaction via LEO"""
    if not LEO_AVAILABLE:
        return jsonify({"error": "LEO not available"})
    
    data = request.json
    interaction_id = leo_manager.monitor_claude_interaction(
        command=data.get('command', ''),
        output=data.get('output', ''),
        files_modified=data.get('files_modified', []),
        success=data.get('success', True),
        context=data.get('context', {})
    )
    
    return jsonify({"interaction_id": interaction_id})

@app.route('/api/leo/generate_claude_md')
def generate_claude_md():
    """Generate CLAUDE.md file via LEO"""
    if not LEO_AVAILABLE:
        return jsonify({"error": "LEO not available"})
    
    claude_md = leo_manager.generate_claude_md()
    if claude_md:
        # Save to file
        with open("CLAUDE_LEO_GENERATED.md", "w") as f:
            f.write(claude_md)
        
        return jsonify({
            "success": True,
            "content": claude_md,
            "file": "CLAUDE_LEO_GENERATED.md"
        })
    else:
        return jsonify({"error": "Failed to generate CLAUDE.md"})

if __name__ == '__main__':
    print("🦁 Starting LeoDock Platform...")
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Initialize LEO system
    leo_initialized = initialize_leo_system()
    
    # Start terminal server in background
    print("📺 Starting terminal server...")
    terminal_thread = threading.Thread(target=start_terminal_server, daemon=True)
    terminal_thread.start()
    
    # Wait for terminal to start
    time.sleep(3)
    
    # Start main dashboard
    print("🚀 Starting dashboard on http://localhost:5001")
    print("📺 Terminal available on http://localhost:5000")
    
    if leo_initialized:
        print("🤖 LEO supervisor monitoring enabled")
        print("🔗 LEO API available at /api/leo/*")
    
    # Open browser automatically
    webbrowser.open('http://localhost:5001')
    
    # Run dashboard server
    app.run(host='0.0.0.0', port=5001, debug=True)