#!/usr/bin/env python3
"""
Test script for internal LM Studio SDK integration
"""

import sys
import os
sys.path.append('src')

def test_internal_lmstudio_import():
    """Test that we can import the internal LM Studio SDK"""
    print("🧪 Testing internal LM Studio SDK import...")
    
    try:
        from src.leodock import lmstudio as lms
        print("✅ Internal LM Studio SDK imported successfully")
        
        # Test basic functions exist
        if hasattr(lms, 'llm'):
            print("✅ llm() function available")
        else:
            print("❌ llm() function not found")
            
        if hasattr(lms, 'Chat'):
            print("✅ Chat class available")
        else:
            print("❌ Chat class not found")
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import internal LM Studio SDK: {e}")
        return False

def test_lmstudio_connection():
    """Test actual connection to LM Studio"""
    print("\n🧪 Testing LM Studio connection...")
    
    try:
        from src.leodock import lmstudio as lms
        
        # Try to get a model
        model = lms.llm()
        print("✅ LM Studio connection established")
        
        # Try to create a chat
        chat = lms.Chat("Test system prompt")
        print("✅ Chat object created")
        
        return True
        
    except Exception as e:
        print(f"❌ LM Studio connection failed: {e}")
        return False

def test_leo_supervisor_integration():
    """Test LEO supervisor with internal SDK"""
    print("\n🧪 Testing LEO supervisor integration...")
    
    try:
        from src.leodock.leo_supervisor import LEOSupervisor
        
        # Try to create LEO supervisor
        leo = LEOSupervisor()
        print("✅ LEO supervisor created with internal SDK")
        
        return True
        
    except Exception as e:
        print(f"❌ LEO supervisor integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing LeoDock Internal LM Studio SDK Integration\n")
    
    results = []
    
    # Run tests
    results.append(test_internal_lmstudio_import())
    results.append(test_lmstudio_connection())
    results.append(test_leo_supervisor_integration())
    
    # Summary
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Internal SDK integration successful.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check the output above.")
        sys.exit(1)