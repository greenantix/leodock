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