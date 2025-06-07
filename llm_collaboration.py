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