"""
Agent Interface System
Standardized interface for AI agents (Claude Code, Copilot, Cline, etc.) 
to communicate with LEO supervisor
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    CLAUDE_CODE = "claude_code"
    COPILOT = "copilot" 
    CLINE = "cline"
    CUSTOM = "custom"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class AgentTask:
    """Standardized task structure for agents"""
    id: str
    description: str
    priority: str  # low, medium, high, critical
    status: TaskStatus
    agent_type: AgentType
    created_at: datetime
    updated_at: datetime
    context: Dict[str, Any]
    dependencies: List[str] = None
    acceptance_criteria: List[str] = None
    estimated_effort: str = None  # small, medium, large
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['agent_type'] = self.agent_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass 
class AgentInteraction:
    """Single interaction between agent and system"""
    id: str
    agent_id: str
    agent_type: AgentType
    timestamp: datetime
    command: str
    output: str
    files_modified: List[str]
    success: bool
    context: Dict[str, Any]
    leo_analysis: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AgentInterface:
    """
    Interface for AI agents to communicate with LEO supervisor
    Handles task management, monitoring, and escalation
    """
    
    def __init__(self, agent_type: AgentType, agent_id: str = None):
        self.agent_type = agent_type
        self.agent_id = agent_id or str(uuid.uuid4())
        self.leo_supervisor = None  # Will be injected
        self.current_tasks: Dict[str, AgentTask] = {}
        self.interaction_history: List[AgentInteraction] = []
        self.monitoring_enabled = True
        
        # Callbacks for agent-specific behavior
        self.on_guidance_received: Optional[Callable] = None
        self.on_escalation: Optional[Callable] = None
        self.on_task_updated: Optional[Callable] = None
        
    def set_leo_supervisor(self, supervisor):
        """Inject LEO supervisor instance"""
        self.leo_supervisor = supervisor
        
    def register_interaction(self, 
                           command: str,
                           output: str,
                           files_modified: List[str] = None,
                           success: bool = True,
                           context: Dict[str, Any] = None) -> str:
        """
        Register an interaction with LEO for monitoring
        
        Returns:
            interaction_id for tracking
        """
        interaction = AgentInteraction(
            id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            timestamp=datetime.now(),
            command=command,
            output=output,
            files_modified=files_modified or [],
            success=success,
            context=context or {}
        )
        
        self.interaction_history.append(interaction)
        
        # Send to LEO for monitoring if enabled and available
        if self.monitoring_enabled and self.leo_supervisor:
            try:
                leo_analysis = self.leo_supervisor.monitor_claude_session({
                    'command': command,
                    'output': output,
                    'files_modified': files_modified or [],
                    'goals': [task.description for task in self.current_tasks.values()],
                    'context': context or {}
                })
                
                interaction.leo_analysis = leo_analysis
                self._process_leo_guidance(leo_analysis)
                
            except Exception as e:
                logger.error(f"Failed to get LEO analysis: {e}")
        
        return interaction.id
    
    def _process_leo_guidance(self, analysis: Dict[str, Any]):
        """Process guidance from LEO supervisor"""
        if not analysis.get("on_track", True):
            logger.warning(f"LEO detected agent off-track: {analysis.get('guidance', '')}")
            
        if analysis.get("intervention_needed"):
            if "escalate_to_opus" in analysis.get("actions", []):
                self._handle_escalation(analysis)
            elif "provide_guidance" in analysis.get("actions", []):
                self._handle_guidance(analysis)
    
    def _handle_guidance(self, analysis: Dict[str, Any]):
        """Handle direct guidance from LEO"""
        guidance = analysis.get("guidance", "")
        logger.info(f"LEO Guidance: {guidance}")
        
        if self.on_guidance_received:
            self.on_guidance_received(guidance, analysis)
    
    def _handle_escalation(self, analysis: Dict[str, Any]):
        """Handle escalation to higher-tier support"""
        logger.warning("LEO escalating issue to Claude Opus")
        
        if self.leo_supervisor:
            escalation_context = {
                'context': f"Agent {self.agent_id} needs assistance",
                'problem': analysis.get('guidance', 'Unspecified issue'),
                'attempted_solutions': [i.command for i in self.interaction_history[-5:]],
                'current_state': {
                    'tasks': [task.to_dict() for task in self.current_tasks.values()],
                    'recent_interactions': len(self.interaction_history)
                }
            }
            
            opus_guidance = self.leo_supervisor.escalate_to_opus(escalation_context)
            
            if opus_guidance and self.on_escalation:
                self.on_escalation(opus_guidance, escalation_context)
    
    def add_task(self, 
                 description: str,
                 priority: str = "medium",
                 context: Dict[str, Any] = None,
                 dependencies: List[str] = None,
                 acceptance_criteria: List[str] = None) -> str:
        """Add a new task for the agent"""
        task = AgentTask(
            id=str(uuid.uuid4()),
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            agent_type=self.agent_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            context=context or {},
            dependencies=dependencies,
            acceptance_criteria=acceptance_criteria
        )
        
        self.current_tasks[task.id] = task
        
        if self.on_task_updated:
            self.on_task_updated(task)
            
        return task.id
    
    def update_task_status(self, task_id: str, status: TaskStatus, context: Dict[str, Any] = None):
        """Update task status"""
        if task_id in self.current_tasks:
            task = self.current_tasks[task_id]
            task.status = status
            task.updated_at = datetime.now()
            
            if context:
                task.context.update(context)
            
            if self.on_task_updated:
                self.on_task_updated(task)
                
            # Remove completed tasks from active list
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                del self.current_tasks[task_id]
    
    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks"""
        return [task for task in self.current_tasks.values() 
                if task.status == TaskStatus.PENDING]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status summary"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'active_tasks': len(self.current_tasks),
            'total_interactions': len(self.interaction_history),
            'monitoring_enabled': self.monitoring_enabled,
            'last_interaction': self.interaction_history[-1].to_dict() if self.interaction_history else None,
            'tasks': [task.to_dict() for task in self.current_tasks.values()]
        }
    
    def request_claude_md_generation(self) -> Optional[str]:
        """Request LEO to generate CLAUDE.md for next phase"""
        if not self.leo_supervisor:
            return None
            
        current_state = {
            'completed_tasks': [i.command for i in self.interaction_history if i.success],
            'current_tasks': [task.description for task in self.current_tasks.values()],
            'issues': [i.command for i in self.interaction_history if not i.success],
            'project_goals': []  # Could be extracted from task context
        }
        
        return self.leo_supervisor.generate_claude_md(current_state)


# Singleton instance for Claude Code
claude_code_interface = AgentInterface(AgentType.CLAUDE_CODE, "claude_code_main")