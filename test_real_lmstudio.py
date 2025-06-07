#!/usr/bin/env python3
"""
Test real LM Studio connection and LEO supervisor
"""

import sys
import time
sys.path.append('src')

def test_lmstudio_connection():
    """Test LM Studio API connection"""
    import lmstudio as lms
    
    print("🔍 Testing LM Studio connection...")
    
    try:
        # Test basic connection
        model = lms.llm()
        print("✅ Connected to LM Studio!")
        
        # Test basic chat
        chat = lms.Chat("You are LEO, a helpful AI supervisor. Respond with just: 'LEO online and ready to supervise!'")
        chat.add_user_message("Status check")
        
        response = model.respond(chat)
        print(f"🤖 LEO Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ LM Studio connection failed: {e}")
        return False

def test_real_leo_supervisor():
    """Test real LEO supervisor with LM Studio"""
    print("\n🧠 Testing Real LEO Supervisor...")
    
    try:
        from leodock.leo_supervisor import LEOSupervisor
        
        # Create real LEO instance
        leo = LEOSupervisor()
        print("✅ Real LEO supervisor created!")
        
        # Test monitoring
        test_interaction = {
            'command': 'python test.py',
            'output': 'Tests passed successfully',
            'files_modified': ['test.py'],
            'goals': ['test the system'],
            'context': {'real_test': True}
        }
        
        result = leo.monitor_claude_session(test_interaction)
        print(f"📊 LEO Analysis: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real LEO supervisor failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Real LM Studio & LEO Test")
    print("=" * 40)
    
    # Test LM Studio connection
    lms_ok = test_lmstudio_connection()
    
    if lms_ok:
        # Test real LEO
        leo_ok = test_real_leo_supervisor()
        
        if leo_ok:
            print("\n🎉 SUCCESS! Real LM Studio + LEO working!")
            print("Ready to switch to MOCK_LEO_SUPERVISOR=false")
        else:
            print("\n⚠️  LM Studio works but LEO supervisor failed")
    else:
        print("\n❌ LM Studio not accessible")
        print("Please start LM Studio server and load a model")