#!/usr/bin/env python3
"""
LM Studio Server Launcher for LeoDock Project
This script starts LM Studio server and manages model loading
"""

import asyncio
import sys
import time
import requests
from pathlib import Path

try:
    import lmstudio
    print(f"LM Studio SDK found. Available: {[x for x in dir(lmstudio) if not x.startswith('_')]}")
except ImportError:
    print("LM Studio SDK not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lmstudio"])
    import lmstudio

class LMStudioManager:
    def __init__(self, port=1234):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.client = None
        
    async def start_server(self):
        """Start LM Studio server using command line"""
        try:
            print("🚀 Starting LM Studio server...")
            
            # Try to connect to existing server first
            if await self.check_server_running():
                print("✅ LM Studio server already running!")
                return True
            
            # Try to start server using the CLI we found earlier
            import subprocess
            import os
            
            lms_path = os.path.expanduser("~/.lmstudio/bin/lms")
            if os.path.exists(lms_path):
                print("🔧 Starting server via LM Studio CLI...")
                # Start server in background
                subprocess.Popen([lms_path, "server", "start", "--port", str(self.port), "--cors"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Wait for server to be ready
                for i in range(30):  # Wait up to 30 seconds
                    if await self.check_server_running():
                        print("✅ LM Studio server started successfully!")
                        return True
                    await asyncio.sleep(1)
                    print(f"⏳ Waiting for server... ({i+1}/30)")
            
            print("❌ Could not start LM Studio server automatically")
            print("💡 Try starting LM Studio GUI manually, then run this script again")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            print("💡 Try starting LM Studio GUI manually, then run this script again")
            return False
    
    async def check_server_running(self):
        """Check if LM Studio server is running"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def list_models(self):
        """List available models via API"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                models = [model['id'] for model in models_data.get('data', [])]
                print("\n📋 Available Models:")
                for i, model in enumerate(models):
                    print(f"  {i+1}. {model}")
                return models
            else:
                print(f"❌ Error listing models: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    async def load_model(self, model_path=None):
        """Load a model via API"""
        try:
            if not model_path:
                models = await self.list_models()
                if not models:
                    print("❌ No models available. Please download a model first.")
                    print("💡 Open LM Studio GUI and download a model from the 'Discover' tab")
                    return False
                model_path = models[0]  # Use first available model
            
            print(f"🔄 Loading model: {model_path}")
            
            # Try to load model via API call
            response = requests.post(
                f"{self.base_url}/v1/models/load",
                json={"model": model_path},
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ Model loaded successfully!")
                return True
            else:
                print(f"❌ Error loading model: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Try loading a model manually in LM Studio GUI")
            return False
    
    async def test_completion(self, prompt="Hello, how are you?"):
        """Test the loaded model with a completion"""
        try:
            print(f"\n🧪 Testing with prompt: '{prompt}'")
            
            response = requests.post(
                f"{self.base_url}/v1/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": 50,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                completion = result['choices'][0]['text']
                print(f"✅ Model response: {completion.strip()}")
                return True
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing completion: {e}")
            return False

async def main():
    """Main function to set up LM Studio for the project"""
    print("🔧 Setting up LM Studio for LeoDock project...")
    
    manager = LMStudioManager()
    
    # Try to start server, but don't fail if it doesn't work
    server_started = await manager.start_server()
    if not server_started:
        print("⚠️  Could not auto-start server, checking if it's already running...")
    
    # List and load models
    if await manager.check_server_running():
        models = await manager.list_models()
        if models:
            await manager.load_model()
            await manager.test_completion()
        else:
            print("\n📥 No models found. To download models:")
            print("   1. Open LM Studio GUI")
            print("   2. Go to 'Discover' tab")
            print("   3. Download a model like 'Meta-Llama-3.1-8B-Instruct'")
            print("   4. Run this script again")
    else:
        print("\n💡 Manual setup required:")
        print("   1. Open LM Studio GUI application")
        print("   2. Go to 'Local Server' tab")
        print("   3. Start the server")
        print("   4. Load a model")
        print("   5. Run this script again to test")
    
    print(f"\n🌐 Server should be at: {manager.base_url}")
    if await manager.check_server_running():
        print("✅ Server is running and ready for Claude Code!")
    else:
        print("❌ Server not running - follow manual setup steps above")
    print("💡 You can now use this endpoint in your LeoDock project!")

if __name__ == "__main__":
    asyncio.run(main())
