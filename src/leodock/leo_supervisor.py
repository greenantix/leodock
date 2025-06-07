"""
LEO Supervisor System
Local LM Studio model that oversees Claude Code and other AI agents
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from . import lmstudio as lms
from anthropic import Anthropic
import logging

# Import LEO visibility system
from .leo_dashboard import (
    log_leo_thought, log_leo_decision, log_leo_monitoring, 
    log_leo_intervention, log_leo_escalation, log_leo_success,
    leo_status
)

logger = logging.getLogger(__name__)


class LEOSupervisor:
    """
    LEO - Local supervisor running on LM Studio
    Monitors and guides Claude Code and other AI agents
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b", anthropic_api_key: str = None):
        log_leo_thought("Initializing LEO supervisor system...")
        
        self.model = lms.llm()  # Connect to default loaded model
        self.chat = lms.Chat(self._get_system_prompt())
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        
        # Monitoring state
        self.session_start = datetime.now()
        self.claude_interactions = []
        self.current_goals = []
        self.dependency_warnings = []
        self.escalation_threshold = 3  # Failed attempts before escalation
        
        log_leo_success("LEO supervisor initialized and ready to monitor agents", {
            "model": model_name,
            "anthropic_enabled": bool(anthropic_api_key),
            "session_start": self.session_start.isoformat()
        })
        
    def _get_system_prompt(self) -> str:
        return """You are LEO, a local AI supervisor running on LM Studio. Your role is to:

1. Monitor Claude Code agent sessions and keep them on track
2. Detect when agents drift from goals or use outdated dependencies  
3. Generate clear task lists and CLAUDE.md files for next development phases
4. Write automated documentation (commits, changelogs, READMEs)
5. Escalate complex issues to Claude Opus when needed
6. Provide context and guidance to keep development productive

Be concise, direct, and focused on keeping the development process efficient."""

    def monitor_claude_session(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor Claude Code interaction and provide guidance
        
        Args:
            interaction_data: {
                'command': str,
                'output': str, 
                'files_modified': List[str],
                'goals': List[str],
                'context': str
            }
            
        Returns:
            Dict with monitoring results and recommendations
        """
        self.claude_interactions.append({
            'timestamp': datetime.now(),
            'data': interaction_data
        })
        
        # Log monitoring activity
        command = interaction_data.get('command', 'N/A')
        files_modified = interaction_data.get('files_modified', [])
        log_leo_monitoring("Claude Code", command, f"Modified {len(files_modified)} files")
        
        # Update status
        leo_status.update_status("analyzing", f"Analyzing command: {command}")
        log_leo_thought(f"Analyzing Claude Code interaction: {command}")
        
        # Analyze interaction
        analysis_prompt = f"""
        Analyze this Claude Code interaction:
        Command: {interaction_data.get('command', 'N/A')}
        Files Modified: {interaction_data.get('files_modified', [])}
        Current Goals: {interaction_data.get('goals', [])}
        
        Assess:
        1. Is Claude staying on track with goals?
        2. Are there any dependency or code quality issues?
        3. Should I intervene or provide guidance?
        
        Respond with JSON: {{"on_track": bool, "intervention_needed": bool, "guidance": str, "priority": "low|medium|high"}}
        """
        
        self.chat.add_user_message(analysis_prompt)
        response = self.model.respond(self.chat)
        self.chat.add_assistant_response(response)
        
        try:
            # Handle both string and PredictionResult objects from LM Studio
            response_text = str(response) if hasattr(response, '__str__') else response
            analysis = json.loads(response_text)
            return self._process_analysis(analysis, interaction_data)
        except json.JSONDecodeError:
            logger.warning(f"LEO response not JSON, using fallback analysis: {response_text[:100]}...")
            # Fallback to simple analysis based on response content
            return self._create_fallback_analysis(response_text, interaction_data)

    def _create_fallback_analysis(self, response_text: str, interaction_data: Dict) -> Dict[str, Any]:
        """Create fallback analysis when LEO doesn't return JSON"""
        
        # Simple keyword-based analysis
        response_lower = response_text.lower()
        
        on_track = True
        intervention_needed = False
        priority = "low"
        guidance = "Continue with current approach"
        
        # Check for error indicators
        if any(word in response_lower for word in ['error', 'problem', 'issue', 'fail', 'wrong']):
            on_track = False
            intervention_needed = True
            priority = "medium"
            guidance = "LEO detected potential issues. Review the output and consider alternative approaches."
        
        # Check for success indicators
        if any(word in response_lower for word in ['success', 'good', 'correct', 'working', 'complete']):
            guidance = "LEO confirms progress is on track. Continue with current approach."
        
        return self._process_analysis({
            "on_track": on_track,
            "intervention_needed": intervention_needed,
            "guidance": guidance,
            "priority": priority
        }, interaction_data)
    
    def _process_analysis(self, analysis: Dict, interaction_data: Dict) -> Dict[str, Any]:
        """Process LEO's analysis and determine actions"""
        
        result = {
            "status": "monitoring",
            "on_track": analysis.get("on_track", True),
            "intervention_needed": analysis.get("intervention_needed", False),
            "guidance": analysis.get("guidance", ""),
            "priority": analysis.get("priority", "low"),
            "actions": []
        }
        
        if analysis.get("intervention_needed"):
            if analysis.get("priority") == "high":
                # Escalate to Claude Opus
                result["actions"].append("escalate_to_opus")
                
            elif analysis.get("priority") == "medium":
                # Direct intervention 
                result["actions"].append("provide_guidance")
                
        return result

    def generate_claude_md(self, current_state: Dict[str, Any]) -> str:
        """
        Generate CLAUDE.md file with next phase instructions
        
        Args:
            current_state: Current project state and goals
        """
        prompt = f"""
        Generate a CLAUDE.md file for the next development phase.
        
        Current State:
        - Completed: {current_state.get('completed_tasks', [])}
        - In Progress: {current_state.get('current_tasks', [])}
        - Issues: {current_state.get('issues', [])}
        - Project Goals: {current_state.get('project_goals', [])}
        
        Create clear, actionable tasks for Claude Code to execute.
        Format as markdown with priority levels and acceptance criteria.
        """
        
        self.chat.add_user_message(prompt)
        response = self.model.respond(self.chat)
        self.chat.add_assistant_response(response)
        
        return str(response)

    def escalate_to_opus(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Escalate complex issues to Claude Opus for guidance
        
        Args:
            context: Full context of the issue needing escalation
        """
        if not self.anthropic_client:
            logger.warning("No Anthropic API key configured for Opus escalation")
            return None
            
        escalation_prompt = f"""
        LEO (local supervisor) is escalating this development issue:
        
        Context: {context.get('context', 'No context provided')}
        Problem: {context.get('problem', 'No problem specified')}
        Attempted Solutions: {context.get('attempted_solutions', [])}
        Current State: {context.get('current_state', {})}
        
        Please provide detailed guidance to get development back on track.
        Focus on specific actionable steps and best practices.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": escalation_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Opus escalation failed: {e}")
            return None

    def generate_commit_message(self, diff_summary: str, files_changed: List[str]) -> str:
        """Generate commit message based on changes"""
        prompt = f"""
        Generate a concise git commit message for these changes:
        
        Files Changed: {files_changed}
        Diff Summary: {diff_summary}
        
        Follow conventional commit format: type(scope): description
        Keep under 50 characters for the subject line.
        """
        
        self.chat.add_user_message(prompt)
        response = self.model.respond(self.chat)
        self.chat.add_assistant_response(response)
        
        return str(response).strip()

    def generate_changelog_entry(self, version: str, changes: List[str]) -> str:
        """Generate changelog entry for version"""
        prompt = f"""
        Generate a changelog entry for version {version}:
        
        Changes: {changes}
        
        Format as proper changelog markdown with Added/Changed/Fixed/Removed sections.
        """
        
        self.chat.add_user_message(prompt)
        response = self.model.respond(self.chat)
        self.chat.add_assistant_response(response)
        
        return str(response)

    def check_dependencies(self, requirements_content: str) -> List[str]:
        """Check for outdated or problematic dependencies"""
        prompt = f"""
        Analyze these Python dependencies for issues:
        
        {requirements_content}
        
        Identify:
        1. Outdated versions
        2. Security vulnerabilities  
        3. Compatibility issues
        4. Missing dependencies
        
        Return as JSON list of warnings.
        """
        
        self.chat.add_user_message(prompt)
        response = self.model.respond(self.chat)
        self.chat.add_assistant_response(response)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return ["Failed to parse dependency analysis"]

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current monitoring session"""
        return {
            "session_duration": str(datetime.now() - self.session_start),
            "total_interactions": len(self.claude_interactions),
            "current_goals": self.current_goals,
            "dependency_warnings": self.dependency_warnings,
            "last_analysis": self.claude_interactions[-1] if self.claude_interactions else None
        }