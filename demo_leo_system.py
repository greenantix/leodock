#!/usr/bin/env python3
"""
Demo LEO System - Show LEO capabilities with mock supervisor
This demonstrates the full autonomous development workflow
"""

import sys
import time
import json
from pathlib import Path

# Setup path
sys.path.append('src')

def demo_leo_monitoring():
    """Demonstrate LEO monitoring Claude Code interactions"""
    
    print("🎯 LEO Monitoring Demo")
    print("=" * 50)
    
    from leodock.leo_manager import leo_manager
    
    # Initialize with mock
    if not leo_manager.initialize():
        print("❌ Failed to initialize LEO")
        return False
    
    print("✅ LEO system initialized\n")
    
    # Simulate Claude Code development session
    print("🤖 Simulating Claude Code development session...")
    
    scenarios = [
        {
            "name": "Successful file edit",
            "command": "edit src/leodock/new_feature.py",
            "output": "File edited successfully. Added 50 lines of code.",
            "files_modified": ["src/leodock/new_feature.py"],
            "success": True,
            "context": {"feature": "user_authentication"}
        },
        {
            "name": "Dependency installation",
            "command": "pip install fastapi uvicorn",
            "output": "Successfully installed fastapi-0.104.1 uvicorn-0.24.0",
            "files_modified": [],
            "success": True,
            "context": {"task": "setup_api"}
        },
        {
            "name": "Test failure",
            "command": "python -m pytest tests/",
            "output": "ERROR: test_authentication.py::test_login - AssertionError",
            "files_modified": [],
            "success": False,
            "context": {"testing": True}
        },
        {
            "name": "Repeated failed command",
            "command": "python -m pytest tests/test_auth.py",
            "output": "ERROR: ModuleNotFoundError: No module named 'auth'",
            "files_modified": [],
            "success": False,
            "context": {"retry_count": 3}
        },
        {
            "name": "Large refactor",
            "command": "refactor authentication system",
            "output": "Refactored 15 files, updated imports and dependencies",
            "files_modified": [f"src/auth/file_{i}.py" for i in range(15)],
            "success": True,
            "context": {"major_change": True}
        }
    ]
    
    interaction_ids = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Command: {scenario['command']}")
        
        interaction_id = leo_manager.monitor_claude_interaction(
            command=scenario['command'],
            output=scenario['output'],
            files_modified=scenario['files_modified'],
            success=scenario['success'],
            context=scenario['context']
        )
        
        interaction_ids.append(interaction_id)
        print(f"   ✅ Monitored with ID: {interaction_id}")
        
        # Add small delay to simulate real development
        time.sleep(0.5)
    
    return interaction_ids


def demo_claude_md_generation():
    """Demonstrate automatic CLAUDE.md generation"""
    
    print("\n📝 CLAUDE.md Generation Demo")
    print("=" * 50)
    
    from leodock.leo_manager import leo_manager
    
    # Generate CLAUDE.md based on session
    print("🤖 LEO analyzing session and generating CLAUDE.md...")
    
    claude_md = leo_manager.generate_claude_md()
    
    if claude_md:
        print("✅ CLAUDE.md generated successfully!")
        
        # Save to demo file
        demo_file = "CLAUDE_DEMO.md"
        with open(demo_file, "w") as f:
            f.write(claude_md)
        
        print(f"📁 Saved to: {demo_file}")
        print("\n📖 Preview:")
        print("-" * 30)
        print(claude_md[:800] + "..." if len(claude_md) > 800 else claude_md)
        print("-" * 30)
        
        return demo_file
    else:
        print("❌ Failed to generate CLAUDE.md")
        return None


def demo_system_status():
    """Demonstrate system status monitoring"""
    
    print("\n📊 System Status Demo")
    print("=" * 50)
    
    from leodock.leo_manager import leo_manager
    
    status = leo_manager.get_system_status()
    
    print("🖥️  LEO System Status:")
    print(json.dumps(status, indent=2))
    
    return status


def demo_commit_message_generation():
    """Demonstrate automatic commit message generation"""
    
    print("\n📝 Commit Message Generation Demo")
    print("=" * 50)
    
    from leodock.leo_manager import leo_manager
    
    # Simulate different types of changes
    scenarios = [
        {
            "files": ["src/leodock/auth.py", "tests/test_auth.py"],
            "diff": "Added user authentication with JWT tokens and tests"
        },
        {
            "files": ["README.md", "docs/setup.md"],
            "diff": "Updated documentation for new authentication system"
        },
        {
            "files": ["requirements.txt", "setup.py"],
            "diff": "Added fastapi and jwt dependencies"
        }
    ]
    
    if leo_manager.leo_supervisor:
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Scenario {i}: {len(scenario['files'])} files changed")
            
            commit_msg = leo_manager.leo_supervisor.generate_commit_message(
                diff_summary=scenario['diff'],
                files_changed=scenario['files']
            )
            
            print(f"   📝 Generated commit: {commit_msg}")
    else:
        print("❌ LEO supervisor not available")


def demo_escalation_scenario():
    """Demonstrate escalation workflow"""
    
    print("\n🆘 Escalation Demo")
    print("=" * 50)
    
    from leodock.leo_manager import leo_manager
    from leodock.escalation_system import EscalationContext, EscalationReason, EscalationLevel
    from datetime import datetime, timedelta
    
    # Simulate escalation scenario
    print("🚨 Simulating high-priority escalation...")
    
    escalation_context = EscalationContext(
        agent_id="claude_code_demo",
        escalation_level=EscalationLevel.LEO_INTERVENTION,
        reason=EscalationReason.REPEATED_FAILURES,
        timestamp=datetime.now(),
        description="Claude Code stuck on authentication implementation after 5 failed attempts",
        current_task="implement JWT authentication",
        failed_attempts=5,
        error_messages=[
            "ModuleNotFoundError: No module named 'jwt'",
            "ImportError: cannot import name 'JWTError'",
            "AttributeError: 'NoneType' object has no attribute 'decode'"
        ],
        recent_commands=[
            "pip install pyjwt",
            "from jwt import decode",
            "python test_auth.py"
        ],
        modified_files=["src/auth.py", "tests/test_auth.py"],
        project_goals=["implement secure authentication", "add user management"],
        time_spent=timedelta(minutes=45),
        completion_percentage=30.0,
        system_state={"cpu": "normal", "memory": "normal"},
        resource_usage={"disk": "85%", "network": "active"},
        previous_escalations=[],
        resolution_attempts=["pip install different jwt library", "check import syntax"]
    )
    
    if leo_manager.escalation_system:
        print("📞 LEO escalating to Claude Opus...")
        
        # This would normally call real Opus, but we'll simulate
        mock_response = """Based on the escalation context, the issue is with JWT library installation and imports.

Immediate Actions:
1. Uninstall any existing JWT packages: pip uninstall jwt pyjwt
2. Install the correct package: pip install PyJWT
3. Use correct import: from jose import jwt (or use PyJWT directly)
4. Check virtual environment activation

Root cause: Conflicting JWT library installations causing import confusion.
Resolution time: 10-15 minutes
"""
        
        print("✅ Opus consultation complete!")
        print(f"📋 Guidance received:\n{mock_response}")
        
        return mock_response
    else:
        print("⚠️  Escalation system not available")
        return None


def main():
    """Run complete LEO system demo"""
    
    print("🚀 LeoDock LEO System Demonstration")
    print("=" * 70)
    print("This demo shows LEO supervising Claude Code autonomously")
    print("=" * 70)
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    try:
        # Demo 1: Monitoring
        interaction_ids = demo_leo_monitoring()
        
        # Demo 2: CLAUDE.md generation
        claude_md_file = demo_claude_md_generation()
        
        # Demo 3: System status
        status = demo_system_status()
        
        # Demo 4: Commit messages
        demo_commit_message_generation()
        
        # Demo 5: Escalation
        escalation_response = demo_escalation_scenario()
        
        # Summary
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("✅ All LEO supervisor functions demonstrated")
        print(f"📊 Monitored {len(interaction_ids)} interactions")
        print(f"📝 Generated CLAUDE.md: {claude_md_file}")
        print(f"🖥️  System Status: {status['leo_supervisor']['type']} mode")
        print("🆘 Escalation workflow tested")
        
        print("\n💡 LEO is ready to supervise real Claude Code sessions!")
        print("🔄 Switch to real LM Studio by setting MOCK_LEO_SUPERVISOR=false")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)