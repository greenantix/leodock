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