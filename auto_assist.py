import os
import time
import requests
import hashlib
from chat_history_manager import ChatHistoryManager

class LeoDockAutoAssist:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.chat_manager = ChatHistoryManager()
        self.seen_files = set()
        self.file_hashes = {}
        self.monitoring = True
        
    def monitor_claude_activity(self):
        """Monitor for new files and automatically get LLM assistance"""
        print("🔍 LeoDock Auto-Assist monitoring started...")
        print("Create any new .py file and Leo will automatically analyze it!")
        print("Modify existing files and get automatic feedback!")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Initialize with current files
        self.seen_files = set(os.listdir('.'))
        for file in self.seen_files:
            if file.endswith('.py'):
                self.file_hashes[file] = self._get_file_hash(file)
        
        try:
            while self.monitoring:
                time.sleep(3)  # Check every 3 seconds
                current_files = set(os.listdir('.'))
                
                # Check for new files
                new_files = current_files - self.seen_files
                for new_file in new_files:
                    if new_file.endswith('.py'):
                        self._analyze_new_file(new_file)
                
                # Check for modified files
                for file in current_files:
                    if file.endswith('.py') and file in self.file_hashes:
                        current_hash = self._get_file_hash(file)
                        if current_hash != self.file_hashes.get(file):
                            self._analyze_modified_file(file)
                            self.file_hashes[file] = current_hash
                
                # Update tracking
                self.seen_files = current_files
                for file in self.seen_files:
                    if file.endswith('.py') and file not in self.file_hashes:
                        self.file_hashes[file] = self._get_file_hash(file)
                        
        except KeyboardInterrupt:
            print("\n🛑 Auto-assist monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
    
    def _get_file_hash(self, filename):
        """Get MD5 hash of file content"""
        try:
            with open(filename, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def _analyze_new_file(self, filename):
        """Analyze newly created Python file"""
        print(f"\n🆕 New Python file detected: {filename}")
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            if len(content.strip()) == 0:
                print(f"⏳ File {filename} is empty, skipping analysis")
                return
                
            # Get Leo's analysis
            leo_analysis = self._get_leo_analysis(filename, content, "new_file")
            
            # Get Archie's embedding
            embedding_len, _ = self._get_archie_embedding(f"New Python file: {filename}\n{content[:200]}")
            
            print(f"🦁 Leo's automatic analysis of {filename}:")
            print(f"   {leo_analysis}")
            print(f"🔍 Archie generated {embedding_len}D embedding for semantic indexing")
            
            # Store the analysis
            self.chat_manager.store_conversation(
                prompt=f"Auto-assist: New file {filename} created",
                response=f"Leo analysis: {leo_analysis}",
                session_id="auto_assist",
                llm_analysis={"type": "new_file_analysis", "filename": filename, "embedding_dimensions": embedding_len},
                metadata={"source": "auto_assist", "file_type": "python", "analysis_type": "new_file"}
            )
                
        except Exception as e:
            print(f"❌ Error analyzing {filename}: {e}")
    
    def _analyze_modified_file(self, filename):
        """Analyze modified Python file"""
        print(f"\n✏️  Modified Python file detected: {filename}")
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            # Get Leo's analysis
            leo_analysis = self._get_leo_analysis(filename, content, "modified_file")
            
            print(f"🦁 Leo's analysis of changes to {filename}:")
            print(f"   {leo_analysis}")
            
            # Store the analysis
            self.chat_manager.store_conversation(
                prompt=f"Auto-assist: File {filename} modified",
                response=f"Leo analysis: {leo_analysis}",
                session_id="auto_assist",
                llm_analysis={"type": "file_modification_analysis", "filename": filename},
                metadata={"source": "auto_assist", "file_type": "python", "analysis_type": "modification"}
            )
                
        except Exception as e:
            print(f"❌ Error analyzing modified {filename}: {e}")
    
    def _get_leo_analysis(self, filename, content, analysis_type):
        """Get Leo's analysis of a Python file"""
        try:
            if analysis_type == "new_file":
                system_prompt = "You are Leo. Claude Code just created a new Python file. Analyze it and provide helpful, concise feedback on its purpose, structure, and potential improvements."
                user_prompt = f"New file: {filename}\n\nContent:\n{content[:1000]}{'...' if len(content) > 1000 else ''}"
            else:
                system_prompt = "You are Leo. Claude Code just modified a Python file. Analyze the current state and provide concise feedback on the code quality and potential improvements."
                user_prompt = f"Modified file: {filename}\n\nCurrent content:\n{content[:1000]}{'...' if len(content) > 1000 else ''}"
            
            response = requests.post(f"{self.base_url}/chat/completions", 
                json={
                    "model": "meta-llama-3.1-8b-instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                })
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Leo communication error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Leo analysis error: {str(e)}"
    
    def _get_archie_embedding(self, text):
        """Get embedding from Archie"""
        try:
            response = requests.post(f"{self.base_url}/embeddings",
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5-embedding",
                    "input": text
                })
            
            if response.status_code == 200:
                embedding = response.json()['data'][0]['embedding']
                return len(embedding), embedding[:3]
            return 0, []
        except:
            return 0, []
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        print("🛑 Auto-assist monitoring stopped")
    
    def get_analysis_summary(self):
        """Get summary of all auto-assist analyses"""
        results = self.chat_manager.search_conversations("Auto-assist")
        
        print(f"\n📊 Auto-Assist Analysis Summary:")
        print(f"   Total analyses performed: {len(results)}")
        
        file_analyses = {}
        for result in results:
            if 'metadata' in result and result['metadata']:
                filename = result['llm_analysis'].get('filename', 'unknown') if result.get('llm_analysis') else 'unknown'
                analysis_type = result['metadata'].get('analysis_type', 'unknown')
                
                if filename not in file_analyses:
                    file_analyses[filename] = []
                file_analyses[filename].append(analysis_type)
        
        print(f"\n📁 Files analyzed:")
        for filename, analyses in file_analyses.items():
            print(f"   - {filename}: {', '.join(set(analyses))}")
        
        return results

# Example usage and testing
if __name__ == "__main__":
    auto_assist = LeoDockAutoAssist()
    
    print("🚀 LeoDock Auto-Assist Demo")
    print("=" * 50)
    
    # Demo mode - create a test file to trigger analysis
    test_file = "demo_test.py"
    
    print(f"Creating demo file: {test_file}")
    with open(test_file, 'w') as f:
        f.write('''def hello_leodock():
    """A simple demo function for LeoDock"""
    print("Hello from LeoDock! 🦁")
    return "LeoDock is awesome!"

if __name__ == "__main__":
    result = hello_leodock()
    print(f"Result: {result}")
''')
    
    print(f"Demo file created. Starting monitoring for 10 seconds...")
    
    # Set up a short monitoring session
    import threading
    import signal
    
    def stop_after_delay():
        time.sleep(10)
        auto_assist.stop_monitoring()
    
    monitor_thread = threading.Thread(target=auto_assist.monitor_claude_activity)
    stop_thread = threading.Thread(target=stop_after_delay)
    
    monitor_thread.start()
    stop_thread.start()
    
    # Wait for monitoring to complete
    monitor_thread.join()
    
    # Show summary
    auto_assist.get_analysis_summary()
    
    # Clean up demo file
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\nDemo file {test_file} cleaned up.")
    
    print("\n✅ Auto-Assist demo complete!")