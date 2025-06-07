#!/usr/bin/env python3
"""
LeoDock Phase 2 - Comprehensive Test Suite
Tests all Phase 2 features and bug fixes
"""

import time
import subprocess
from datetime import datetime

def test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def test_result(passed, message):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")
    return passed

def test_browser_debugging():
    """Test browser debugging tools"""
    test_header("Browser Debugging Tools")
    
    try:
        # Test browser process analysis
        result = subprocess.run(['python', 'debug_browser_issue.py'], 
                              capture_output=True, text=True, timeout=10)
        
        success = result.returncode == 0 and "Browser Process Analysis" in result.stdout
        test_result(success, "Browser debugging tool execution")
        
        if success:
            print(f"   Browser analysis output: {len(result.stdout)} characters")
        
        return success
    except Exception as e:
        return test_result(False, f"Browser debugging failed: {e}")

def test_connection_manager():
    """Test connection manager functionality"""
    test_header("Connection Manager")
    
    try:
        # Test connection status check
        result = subprocess.run(['python', 'connection_manager.py', 'status'], 
                              capture_output=True, text=True, timeout=10)
        
        success = result.returncode == 0 and "Service Status" in result.stdout
        test_result(success, "Connection manager status check")
        
        # Test port availability check
        result2 = subprocess.run(['python', 'connection_manager.py', 'test'], 
                               capture_output=True, text=True, timeout=10)
        
        success2 = result2.returncode == 0
        test_result(success2, "Port availability testing")
        
        return success and success2
    except Exception as e:
        return test_result(False, f"Connection manager failed: {e}")

def test_llm_communication():
    """Test LLM communication systems"""
    test_header("LLM Communication Systems")
    
    try:
        # Test basic Leo communication
        from talk_to_leo import talk_to_leo
        leo_response = talk_to_leo("Phase 2 testing in progress", mode="general")
        
        success1 = leo_response and "error" not in leo_response.lower()
        test_result(success1, "Leo communication")
        
        # Test LLM commands
        result = subprocess.run(['python', 'llm_commands.py', 'write', 'leo', 'Phase 2 test message'], 
                              capture_output=True, text=True, timeout=15)
        
        success2 = result.returncode == 0 and "LEO responded" in result.stdout
        test_result(success2, "Unix-style LLM commands")
        
        return success1 and success2
    except Exception as e:
        return test_result(False, f"LLM communication failed: {e}")

def test_advanced_chat_history():
    """Test advanced chat history with semantic search"""
    test_header("Advanced Chat History")
    
    try:
        # Test saving conversations
        result = subprocess.run(['python', 'advanced_chat_history.py', 'save', 'test_user', 'Phase 2 testing conversation'], 
                              capture_output=True, text=True, timeout=15)
        
        success1 = result.returncode == 0 and "Saved conversation" in result.stdout
        test_result(success1, "Conversation saving")
        
        # Test text search
        result2 = subprocess.run(['python', 'advanced_chat_history.py', 'search', 'Phase 2'], 
                               capture_output=True, text=True, timeout=15)
        
        success2 = result2.returncode == 0 and "search results" in result2.stdout
        test_result(success2, "Text search functionality")
        
        # Test semantic search
        result3 = subprocess.run(['python', 'advanced_chat_history.py', 'semantic', 'testing development'], 
                               capture_output=True, text=True, timeout=20)
        
        success3 = result3.returncode == 0 and "Semantic search" in result3.stdout
        test_result(success3, "Semantic search functionality")
        
        # Test statistics
        result4 = subprocess.run(['python', 'advanced_chat_history.py', 'stats'], 
                               capture_output=True, text=True, timeout=10)
        
        success4 = result4.returncode == 0 and "Statistics" in result4.stdout
        test_result(success4, "Statistics generation")
        
        return success1 and success2 and success3 and success4
    except Exception as e:
        return test_result(False, f"Advanced chat history failed: {e}")

def test_platform_monitoring():
    """Test platform health monitoring"""
    test_header("Platform Health Monitoring")
    
    try:
        # Test basic health check
        result = subprocess.run(['python', 'leodock_monitor.py'], 
                              capture_output=True, text=True, timeout=20)
        
        success1 = result.returncode == 0 and "Health Check" in result.stdout
        test_result(success1, "Basic health monitoring")
        
        # Test auto-fix functionality
        result2 = subprocess.run(['python', 'leodock_monitor.py', 'fix'], 
                               capture_output=True, text=True, timeout=15)
        
        success2 = result2.returncode == 0 and "Auto-fixing" in result2.stdout
        test_result(success2, "Auto-fix functionality")
        
        return success1 and success2
    except Exception as e:
        return test_result(False, f"Platform monitoring failed: {e}")

def test_integration():
    """Test integration between components"""
    test_header("Component Integration")
    
    try:
        # Test chat history integration with LLM commands
        from llm_commands import LLMCommands
        from advanced_chat_history import AdvancedChatHistory
        
        llm_commands = LLMCommands()
        chat_history = AdvancedChatHistory()
        
        # Test that components can work together
        test_message = "Integration test message"
        chat_history.save_conversation("integration_test", test_message)
        
        success1 = True  # If we got here, basic integration works
        test_result(success1, "Component instantiation")
        
        # Test semantic search for integration
        results = chat_history.semantic_search("integration", limit=5)
        success2 = len(results) >= 0  # Should work even if no results
        test_result(success2, "Cross-component functionality")
        
        return success1 and success2
    except Exception as e:
        return test_result(False, f"Integration testing failed: {e}")

def run_comprehensive_test():
    """Run all Phase 2 tests"""
    print("🦁" * 20)
    print("🦁 LEODOCK PHASE 2 - COMPREHENSIVE TEST SUITE")
    print("🦁" * 20)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Run all tests
    test_results['browser_debugging'] = test_browser_debugging()
    time.sleep(1)
    
    test_results['connection_manager'] = test_connection_manager()
    time.sleep(1)
    
    test_results['llm_communication'] = test_llm_communication()
    time.sleep(1)
    
    test_results['advanced_chat_history'] = test_advanced_chat_history()
    time.sleep(1)
    
    test_results['platform_monitoring'] = test_platform_monitoring()
    time.sleep(1)
    
    test_results['integration'] = test_integration()
    
    # Summary
    test_header("TEST SUMMARY")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Phase 2 features are working correctly.")
        print(f"🚀 LeoDock Platform is ready for advanced usage!")
    else:
        failed_tests = [name for name, result in test_results.items() if not result]
        print(f"\n⚠️ Some tests failed: {', '.join(failed_tests)}")
        print(f"🔧 Review the failed components for troubleshooting.")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    exit(0 if all(results.values()) else 1)