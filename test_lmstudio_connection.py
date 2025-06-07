#!/usr/bin/env python3
"""
Test LM Studio connection and available models
"""

import lmstudio as lms
import json
import sys


def test_lmstudio_connection():
    """Test connection to LM Studio and list available models"""
    
    print("🔍 Testing LM Studio connection...")
    
    try:
        # Try to connect to LM Studio
        print("📡 Connecting to LM Studio...")
        
        # List available models
        print("📋 Checking available models...")
        
        # Test basic model initialization
        try:
            model = lms.llm()
            print("✅ Successfully connected to LM Studio!")
            print(f"📦 Model instance created: {type(model)}")
            
            # Test basic chat functionality
            print("💬 Testing basic chat functionality...")
            chat = lms.Chat("You are a helpful assistant. Reply with just 'Hello from LEO!'")
            chat.add_user_message("Say hello")
            
            try:
                response = model.respond(chat)
                print(f"🎯 Model response: {response}")
                print("✅ LM Studio is fully functional!")
                return True
                
            except Exception as e:
                print(f"⚠️  Model response failed: {e}")
                print("💡 This might mean no model is loaded in LM Studio")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create model instance: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to LM Studio: {e}")
        print("💡 Make sure LM Studio is running and has a model loaded")
        return False


def test_leo_supervisor_basic():
    """Test basic LEO supervisor functionality"""
    
    print("\n🤖 Testing LEO supervisor basic functionality...")
    
    try:
        # Import our LEO supervisor
        sys.path.append('src')
        from leodock.leo_supervisor import LEOSupervisor
        
        print("📦 LEOSupervisor class imported successfully")
        
        # Create LEO instance
        leo = LEOSupervisor()
        print("✅ LEO supervisor instance created")
        
        # Test basic monitoring
        test_interaction = {
            'command': 'test command',
            'output': 'test output',
            'files_modified': ['test.py'],
            'goals': ['test goal'],
            'context': {'test': 'data'}
        }
        
        print("🔍 Testing interaction monitoring...")
        result = leo.monitor_claude_session(test_interaction)
        print(f"📊 Monitoring result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ LEO supervisor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 LeoDock System Test")
    print("=" * 50)
    
    # Test LM Studio connection
    lmstudio_ok = test_lmstudio_connection()
    
    # Test LEO supervisor
    leo_ok = test_leo_supervisor_basic()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   LM Studio: {'✅ OK' if lmstudio_ok else '❌ FAILED'}")
    print(f"   LEO Supervisor: {'✅ OK' if leo_ok else '❌ FAILED'}")
    
    if lmstudio_ok and leo_ok:
        print("\n🎉 All tests passed! LeoDock is ready!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)