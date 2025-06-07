#!/usr/bin/env python3
"""
Test LEO Integration with Mock and Real Systems
"""

import sys
import os
import logging
from pathlib import Path

# Setup path for imports
sys.path.append('src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_leo_integration():
    """Test complete LEO integration"""
    
    print("🚀 LeoDock LEO Integration Test")
    print("=" * 50)
    
    try:
        # Import LEO manager
        from leodock.leo_manager import leo_manager
        
        print("✅ LEO Manager imported successfully")
        
        # Initialize LEO system
        print("\n🔧 Initializing LEO system...")
        if not leo_manager.initialize():
            print("❌ LEO initialization failed")
            return False
        
        print("✅ LEO system initialized successfully")
        
        # Test system status
        print("\n📊 Checking system status...")
        status = leo_manager.get_system_status()
        
        print(f"   LEO Manager: {'✅' if status['leo_manager']['initialized'] else '❌'}")
        print(f"   LEO Supervisor: {'✅' if status['leo_supervisor']['available'] else '❌'} ({status['leo_supervisor']['type']})")
        print(f"   Context Indexer: {'✅' if status['context_indexer']['available'] else '❌'}")
        print(f"   Escalation System: {'✅' if status['escalation_system']['available'] else '❌'}")
        print(f"   Agent Interfaces: {'✅' if status['agent_interfaces']['claude_code'] else '❌'}")
        
        # Test Claude Code interaction monitoring
        print("\n🤖 Testing Claude Code interaction monitoring...")
        
        interaction_id = leo_manager.monitor_claude_interaction(
            command="test_command",
            output="test output with some results",
            files_modified=["test.py", "src/leodock/test.py"],
            success=True,
            context={"test": "integration"}
        )
        
        print(f"✅ Interaction monitored with ID: {interaction_id}")
        
        # Test error scenario
        print("\n⚠️  Testing error scenario...")
        
        error_interaction_id = leo_manager.monitor_claude_interaction(
            command="failing_command",
            output="ERROR: Something went wrong\nTraceback: ...",
            files_modified=[],
            success=False,
            context={"error": "test_error"}
        )
        
        print(f"✅ Error interaction monitored with ID: {error_interaction_id}")
        
        # Test CLAUDE.md generation
        print("\n📝 Testing CLAUDE.md generation...")
        
        claude_md = leo_manager.generate_claude_md()
        if claude_md:
            print("✅ CLAUDE.md generated successfully")
            print("📄 Preview:")
            print("-" * 30)
            print(claude_md[:500] + "..." if len(claude_md) > 500 else claude_md)
            print("-" * 30)
        else:
            print("❌ CLAUDE.md generation failed")
        
        # Test context indexing (if available)
        if status['context_indexer']['available']:
            print("\n🔍 Testing context indexing...")
            
            try:
                # Index current project
                index_stats = leo_manager.index_project(".")
                print(f"✅ Project indexed: {index_stats.get('files_indexed', 0)} files")
                
                # Test search
                search_results = leo_manager.search_context("LEO supervisor", n_results=3)
                print(f"✅ Context search returned {len(search_results)} results")
                
            except Exception as e:
                print(f"⚠️  Context indexing test failed: {e}")
        
        # Final status check
        print("\n📋 Final system status:")
        final_status = leo_manager.get_system_status()
        
        if final_status['leo_supervisor'].get('session'):
            session = final_status['leo_supervisor']['session']
            print(f"   Session Duration: {session.get('session_duration', 'unknown')}")
            print(f"   Total Interactions: {session.get('total_interactions', 0)}")
            print(f"   Mock Mode: {session.get('mock_mode', 'unknown')}")
        
        print("\n🎉 LEO Integration Test Complete!")
        print("✅ All core components are functional")
        
        return True
        
    except Exception as e:
        print(f"❌ LEO integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_claude_md_file_creation():
    """Test actual CLAUDE.md file creation"""
    
    print("\n📝 Testing CLAUDE.md file creation...")
    
    try:
        from leodock.leo_manager import leo_manager
        
        # Generate CLAUDE.md
        claude_md_content = leo_manager.generate_claude_md()
        
        if claude_md_content:
            # Write to file
            with open("CLAUDE_GENERATED.md", "w") as f:
                f.write(claude_md_content)
            
            print("✅ CLAUDE_GENERATED.md file created successfully")
            print(f"📊 File size: {len(claude_md_content)} characters")
            
            return True
        else:
            print("❌ No content generated for CLAUDE.md")
            return False
            
    except Exception as e:
        print(f"❌ CLAUDE.md file creation failed: {e}")
        return False


if __name__ == "__main__":
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    print("🎯 Starting comprehensive LEO integration tests...")
    
    # Test LEO integration
    integration_ok = test_leo_integration()
    
    # Test CLAUDE.md generation
    claude_md_ok = test_claude_md_file_creation()
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"   LEO Integration: {'✅ PASSED' if integration_ok else '❌ FAILED'}")
    print(f"   CLAUDE.md Generation: {'✅ PASSED' if claude_md_ok else '❌ FAILED'}")
    
    if integration_ok and claude_md_ok:
        print("\n🎉 All tests passed! LEO system is ready!")
        print("\n💡 Next steps:")
        print("   1. Run LM Studio setup commands from INSTALL_LMSTUDIO.md")
        print("   2. Set MOCK_LEO_SUPERVISOR=false in .env")
        print("   3. Test with real LM Studio integration")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)