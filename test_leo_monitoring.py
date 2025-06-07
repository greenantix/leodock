#!/usr/bin/env python3
"""
Test LEO monitoring with internal SDK
"""

import sys
import json
sys.path.append('src')

def test_leo_monitoring():
    """Test LEO monitoring a Claude Code interaction"""
    print("🧪 Testing LEO monitoring with internal SDK...")
    
    try:
        from src.leodock.leo_supervisor import LEOSupervisor
        
        # Create LEO supervisor with internal SDK
        leo = LEOSupervisor()
        print("✅ LEO supervisor created")
        
        # Test monitoring interaction
        interaction_data = {
            'command': 'git status',
            'output': 'On branch main\nnothing to commit, working tree clean',
            'files_modified': [],
            'goals': ['test LEO monitoring'],
            'context': 'Testing internal SDK integration'
        }
        
        print("📡 Monitoring Claude interaction...")
        result = leo.monitor_claude_session(interaction_data)
        
        print(f"✅ LEO analysis result: {result}")
        
        # Test generating CLAUDE.md
        print("📝 Testing CLAUDE.md generation...")
        current_state = {
            'completed_tasks': ['Internal SDK integration'],
            'current_tasks': ['Testing LEO monitoring'],
            'issues': ['None'],
            'project_goals': ['Autonomous AI development platform']
        }
        
        claude_md = leo.generate_claude_md(current_state)
        print(f"✅ CLAUDE.md generated: {len(claude_md)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ LEO monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing LEO Monitoring with Internal LM Studio SDK\n")
    
    success = test_leo_monitoring()
    
    if success:
        print("\n🎉 LEO monitoring test successful! Internal SDK fully integrated.")
    else:
        print("\n💥 LEO monitoring test failed.")
    
    sys.exit(0 if success else 1)