#!/usr/bin/env python3
"""
Start LM Studio server via CLI and test connection
"""

import subprocess
import time
import requests
import json
import os
from pathlib import Path


def start_lmstudio_server():
    """Start LM Studio server in background"""
    
    lms_path = Path.home() / ".lmstudio" / "bin" / "lms"
    
    if not lms_path.exists():
        print(f"❌ LM Studio CLI not found at {lms_path}")
        return False
    
    try:
        print("🚀 Starting LM Studio server...")
        
        # Try to start server in background
        result = subprocess.run([str(lms_path), "server", "start", "--host", "0.0.0.0", "--port", "1234"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Failed to start server: {result.stderr}")
            return False
            
        print("✅ Server start command executed")
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Server start command timed out (this might be normal)")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False


def load_model():
    """Load a model in LM Studio"""
    
    lms_path = Path.home() / ".lmstudio" / "bin" / "lms"
    
    # Try to load the Llama model we found
    model_path = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
    
    try:
        print(f"📦 Loading model: {model_path}")
        
        result = subprocess.run([str(lms_path), "load", model_path], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Model loaded successfully")
            return True
        else:
            print(f"❌ Failed to load model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Model loading timed out")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def test_api_connection():
    """Test API connection to LM Studio"""
    
    base_url = "http://localhost:1234"
    
    try:
        print("🔍 Testing API connection...")
        
        # Test health endpoint
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ API connection successful!")
            print(f"📋 Available models: {json.dumps(models, indent=2)}")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        print("❌ Could not connect to LM Studio API")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False


def main():
    """Main function to start and test LM Studio"""
    
    print("🎯 LM Studio Setup & Test")
    print("=" * 40)
    
    # Start server
    server_started = start_lmstudio_server()
    
    if server_started:
        # Wait a bit for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(5)
        
        # Load model
        model_loaded = load_model()
        
        if model_loaded:
            # Wait for model to load
            print("⏳ Waiting for model to load...")
            time.sleep(10)
            
            # Test API
            api_ok = test_api_connection()
            
            if api_ok:
                print("\n🎉 LM Studio is ready for LEO!")
                return True
    
    print("\n💡 Manual steps needed:")
    print("1. Open LM Studio GUI")
    print("2. Go to 'Developer' tab")
    print("3. Start local server")
    print("4. Load a model (Llama 3.1 8B recommended)")
    print("5. Run this test again")
    
    return False


if __name__ == "__main__":
    main()