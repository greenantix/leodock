import requests
import json
import time
from chat_history_manager import ChatHistoryManager

class LLMCommunicationHub:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.message_history = []
        self.chat_manager = ChatHistoryManager()
    
    def leo_to_archie(self, leo_message):
        """Leo sends a message to be processed by Archie"""
        print(f"📤 Leo → Archie: {leo_message}")
        
        # Get embedding from Archie
        embedding_len, sample = self.ask_archie_for_embedding(leo_message)
        
        if embedding_len > 0:
            # Send Archie's response back to Leo
            leo_response = self.ask_leo_about_embedding(leo_message, embedding_len)
            
            print(f"📥 Archie → Leo: Embedding generated ({embedding_len} dimensions)")
            print(f"📥 Leo's response: {leo_response}")
            
            # Store this communication in history
            self.chat_manager.store_conversation(
                prompt=f"Leo to Archie: {leo_message}",
                response=f"Archie embedding: {embedding_len}D, Leo response: {leo_response}",
                session_id="llm_communication",
                llm_analysis={"type": "leo_to_archie", "embedding_dimensions": embedding_len},
                metadata={"communication_type": "inter_llm", "participants": ["leo", "archie"]}
            )
            
            return leo_response
        else:
            print(f"❌ Archie communication failed: {sample}")
            return "Communication error"
    
    def archie_to_leo(self, text_for_embedding, question_for_leo):
        """Archie processes text, then Leo analyzes the result"""
        print(f"🔍 Archie processing: {text_for_embedding}")
        
        # Get embedding from Archie
        embedding_len, sample = self.ask_archie_for_embedding(text_for_embedding)
        
        if embedding_len > 0:
            print(f"📊 Archie generated {embedding_len}D embedding")
            
            # Ask Leo to interpret the embedding result
            leo_response = self.ask_leo(f"Archie generated a {embedding_len}-dimensional embedding for the text: '{text_for_embedding}'. {question_for_leo}")
            
            print(f"🦁 Leo's analysis: {leo_response}")
            
            # Store communication
            self.chat_manager.store_conversation(
                prompt=f"Archie embedding for: {text_for_embedding}",
                response=f"Leo analysis: {leo_response}",
                session_id="llm_communication",
                llm_analysis={"type": "archie_to_leo", "embedding_dimensions": embedding_len},
                metadata={"communication_type": "inter_llm", "participants": ["archie", "leo"]}
            )
            
            return leo_response
        else:
            return f"Archie error: {sample}"
    
    def ask_archie_for_embedding(self, text):
        """Get embeddings from Archie"""
        try:
            response = requests.post(f"{self.base_url}/embeddings",
                json={"model": "text-embedding-nomic-embed-text-v1.5-embedding", "input": text})
            
            if response.status_code == 200:
                embedding = response.json()['data'][0]['embedding']
                return len(embedding), embedding[:3]
            return 0, f"HTTP {response.status_code}"
        except Exception as e:
            return 0, str(e)
    
    def ask_leo(self, question):
        """Send question to Leo"""
        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                json={
                    "model": "meta-llama-3.1-8b-instruct",
                    "messages": [
                        {"role": "system", "content": "You are Leo in LeoDock. You work with Claude Code and Archie. Be helpful and concise."},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                })
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Leo error: HTTP {response.status_code}"
        except Exception as e:
            return f"Leo error: {str(e)}"
    
    def ask_leo_about_embedding(self, original_text, embedding_length):
        """Ask Leo to analyze embedding results"""
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
    
    def three_way_collaboration(self, task_description):
        """All three AIs collaborate on a complex task"""
        print(f"\n🤖 Three-Way AI Collaboration")
        print(f"📋 Task: {task_description}")
        print("=" * 60)
        
        # Step 1: Claude Code initial analysis
        print(f"\n🤖 Claude Code (Phase 1): Initial Analysis")
        claude_analysis = f"Analyzing task: {task_description}. Breaking down into components for Leo and Archie."
        print(f"Claude: {claude_analysis}")
        
        # Step 2: Get Archie's semantic understanding
        print(f"\n🔍 Archie (Phase 2): Semantic Analysis")
        embedding_len, sample = self.ask_archie_for_embedding(task_description)
        archie_result = f"Generated {embedding_len}D semantic embedding" if embedding_len > 0 else "Embedding failed"
        print(f"Archie: {archie_result}")
        
        # Step 3: Leo analyzes based on Archie's results
        print(f"\n🦁 Leo (Phase 3): Strategic Analysis")
        leo_question = f"Based on Archie's {embedding_len}D embedding of '{task_description}', provide a strategic implementation plan."
        leo_response = self.ask_leo(leo_question)
        print(f"Leo: {leo_response}")
        
        # Step 4: Claude Code synthesis
        print(f"\n🤖 Claude Code (Phase 4): Synthesis & Action Plan")
        claude_synthesis = f"Combining insights: Archie's semantic analysis ({embedding_len}D) + Leo's strategy. Ready to implement."
        print(f"Claude: {claude_synthesis}")
        
        # Store the complete collaboration
        full_conversation = f"Claude: {claude_analysis}\nArchie: {archie_result}\nLeo: {leo_response}\nClaude: {claude_synthesis}"
        self.chat_manager.store_conversation(
            prompt=f"Three-way collaboration: {task_description}",
            response=full_conversation,
            session_id="three_way_collaboration",
            llm_analysis={"type": "three_way", "participants": ["claude", "archie", "leo"], "embedding_dimensions": embedding_len},
            metadata={"collaboration_type": "full_team", "task_complexity": "high"}
        )
        
        print(f"\n✅ Three-way collaboration complete! Stored in conversation history.")
        return {
            "claude_analysis": claude_analysis,
            "archie_result": archie_result,
            "leo_response": leo_response,
            "claude_synthesis": claude_synthesis
        }

# Example usage and testing
if __name__ == "__main__":
    hub = LLMCommunicationHub()
    
    print("🚀 Testing LLM Communication Hub\n")
    
    # Test 1: Leo to Archie communication
    print("=" * 50)
    print("TEST 1: Leo to Archie Communication")
    print("=" * 50)
    hub.leo_to_archie("We need to create a semantic search system for LeoDock")
    
    time.sleep(1)
    
    # Test 2: Archie to Leo communication
    print("\n" + "=" * 50)
    print("TEST 2: Archie to Leo Communication")
    print("=" * 50)
    hub.archie_to_leo(
        "Claude Code integration with LeoDock platform", 
        "How can we use this embedding to improve the development workflow?"
    )
    
    time.sleep(1)
    
    # Test 3: Three-way collaboration
    print("\n" + "=" * 50)
    print("TEST 3: Three-Way Collaboration")
    print("=" * 50)
    result = hub.three_way_collaboration("Build an intelligent code review system that learns from developer patterns")
    
    # Show conversation history stats
    print(f"\n📊 Communication Statistics:")
    stats = hub.chat_manager.get_statistics()
    print(f"  - Total conversations: {stats['total_conversations']}")
    print(f"  - Total embeddings: {stats['total_embeddings']}")
    print(f"  - Unique tokens: {stats['unique_tokens']}")
    
    # Show recent communications
    print(f"\n📋 Recent Communications:")
    recent = hub.chat_manager.get_recent_conversations(3)
    for i, conv in enumerate(recent, 1):
        print(f"  {i}. {conv['timestamp']}: {conv['prompt'][:60]}...")