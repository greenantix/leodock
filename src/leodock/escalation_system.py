"""
Multi-Tier Escalation System
LEO -> Claude Opus -> Human escalation chain with context preservation
"""

import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import base64
from pathlib import Path

logger = logging.getLogger(__name__)


class EscalationLevel(Enum):
    LEO_MONITORING = "leo_monitoring"
    LEO_INTERVENTION = "leo_intervention" 
    OPUS_CONSULTATION = "opus_consultation"
    HUMAN_REQUIRED = "human_required"
    REMOTE_ACCESS = "remote_access"


class EscalationReason(Enum):
    STUCK_ON_TASK = "stuck_on_task"
    REPEATED_FAILURES = "repeated_failures"
    DEPENDENCY_ISSUES = "dependency_issues"
    GOAL_DRIFT = "goal_drift"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    CRITICAL_ERROR = "critical_error"
    SYSTEM_INSTABILITY = "system_instability"


@dataclass
class EscalationContext:
    """Complete context for escalation decisions"""
    agent_id: str
    escalation_level: EscalationLevel
    reason: EscalationReason
    timestamp: datetime
    description: str
    
    # Technical context
    current_task: Optional[str]
    failed_attempts: int
    error_messages: List[str]
    recent_commands: List[str]
    modified_files: List[str]
    
    # Project context
    project_goals: List[str]
    time_spent: timedelta
    completion_percentage: float
    
    # System context
    system_state: Dict[str, Any]
    resource_usage: Dict[str, Any]
    
    # Previous escalations
    previous_escalations: List[str]
    resolution_attempts: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['escalation_level'] = self.escalation_level.value
        data['reason'] = self.reason.value
        data['timestamp'] = self.timestamp.isoformat()
        data['time_spent'] = str(self.time_spent)
        return data


@dataclass
class EscalationResponse:
    """Response from escalation tier"""
    level: EscalationLevel
    success: bool
    guidance: str
    action_items: List[str]
    estimated_resolution_time: Optional[str]
    requires_further_escalation: bool
    context_updates: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['level'] = self.level.value
        return data


class EscalationSystem:
    """
    Manages multi-tier escalation from LEO supervision to human intervention
    """
    
    def __init__(self, 
                 leo_supervisor=None,
                 anthropic_client=None,
                 notification_webhook: str = None,
                 remote_access_url: str = None):
        
        self.leo_supervisor = leo_supervisor
        self.anthropic_client = anthropic_client
        self.notification_webhook = notification_webhook
        self.remote_access_url = remote_access_url
        
        # Escalation thresholds
        self.escalation_thresholds = {
            EscalationReason.STUCK_ON_TASK: 3,          # 3 failed attempts
            EscalationReason.REPEATED_FAILURES: 5,      # 5 consecutive failures
            EscalationReason.DEPENDENCY_ISSUES: 2,      # 2 dependency problems
            EscalationReason.GOAL_DRIFT: 1,             # Immediate escalation
            EscalationReason.TIMEOUT_EXCEEDED: 1,       # Immediate escalation
            EscalationReason.CRITICAL_ERROR: 1,         # Immediate escalation
        }
        
        # Escalation tracking
        self.active_escalations: Dict[str, EscalationContext] = {}
        self.escalation_history: List[EscalationContext] = []
        
        # Callbacks for notifications
        self.on_escalation: Optional[Callable] = None
        self.on_resolution: Optional[Callable] = None
        
    def evaluate_escalation(self, 
                          agent_id: str,
                          current_context: Dict[str, Any]) -> Optional[EscalationContext]:
        """
        Evaluate if escalation is needed based on current context
        
        Args:
            agent_id: ID of the agent needing evaluation
            current_context: Current agent and system context
            
        Returns:
            EscalationContext if escalation is needed, None otherwise
        """
        
        # Analyze context for escalation triggers
        escalation_reason = self._analyze_escalation_triggers(current_context)
        
        if not escalation_reason:
            return None
            
        # Determine escalation level
        escalation_level = self._determine_escalation_level(escalation_reason, current_context)
        
        # Create escalation context
        context = EscalationContext(
            agent_id=agent_id,
            escalation_level=escalation_level,
            reason=escalation_reason,
            timestamp=datetime.now(),
            description=self._generate_escalation_description(escalation_reason, current_context),
            current_task=current_context.get('current_task'),
            failed_attempts=current_context.get('failed_attempts', 0),
            error_messages=current_context.get('error_messages', []),
            recent_commands=current_context.get('recent_commands', []),
            modified_files=current_context.get('modified_files', []),
            project_goals=current_context.get('project_goals', []),
            time_spent=timedelta(seconds=current_context.get('time_spent_seconds', 0)),
            completion_percentage=current_context.get('completion_percentage', 0.0),
            system_state=current_context.get('system_state', {}),
            resource_usage=current_context.get('resource_usage', {}),
            previous_escalations=self._get_previous_escalations(agent_id),
            resolution_attempts=current_context.get('resolution_attempts', [])
        )
        
        return context
    
    def _analyze_escalation_triggers(self, context: Dict[str, Any]) -> Optional[EscalationReason]:
        """Analyze context for escalation triggers"""
        
        # Check for repeated failures
        if context.get('consecutive_failures', 0) >= self.escalation_thresholds[EscalationReason.REPEATED_FAILURES]:
            return EscalationReason.REPEATED_FAILURES
            
        # Check for task being stuck
        if context.get('failed_attempts', 0) >= self.escalation_thresholds[EscalationReason.STUCK_ON_TASK]:
            return EscalationReason.STUCK_ON_TASK
            
        # Check for timeout
        time_spent = context.get('time_spent_seconds', 0)
        if time_spent > 3600:  # 1 hour
            return EscalationReason.TIMEOUT_EXCEEDED
            
        # Check for critical errors
        error_messages = context.get('error_messages', [])
        critical_keywords = ['fatal', 'critical', 'corruption', 'segfault', 'memory']
        if any(keyword in ' '.join(error_messages).lower() for keyword in critical_keywords):
            return EscalationReason.CRITICAL_ERROR
            
        # Check for goal drift (based on LEO analysis)
        if context.get('goal_drift_detected', False):
            return EscalationReason.GOAL_DRIFT
            
        # Check for dependency issues
        if context.get('dependency_errors', 0) >= self.escalation_thresholds[EscalationReason.DEPENDENCY_ISSUES]:
            return EscalationReason.DEPENDENCY_ISSUES
            
        return None
    
    def _determine_escalation_level(self, 
                                   reason: EscalationReason, 
                                   context: Dict[str, Any]) -> EscalationLevel:
        """Determine appropriate escalation level"""
        
        # High-priority reasons go straight to Opus
        if reason in [EscalationReason.CRITICAL_ERROR, EscalationReason.SYSTEM_INSTABILITY]:
            return EscalationLevel.OPUS_CONSULTATION
            
        # Check if LEO has already intervened
        if context.get('leo_intervention_attempts', 0) > 0:
            return EscalationLevel.OPUS_CONSULTATION
            
        # Check if this is a repeated escalation
        agent_id = context.get('agent_id')
        if agent_id and self._has_recent_escalations(agent_id):
            return EscalationLevel.OPUS_CONSULTATION
            
        # Default to LEO intervention first
        return EscalationLevel.LEO_INTERVENTION
    
    def _generate_escalation_description(self, 
                                       reason: EscalationReason, 
                                       context: Dict[str, Any]) -> str:
        """Generate human-readable escalation description"""
        
        descriptions = {
            EscalationReason.STUCK_ON_TASK: f"Agent stuck on task '{context.get('current_task', 'unknown')}' after {context.get('failed_attempts', 0)} attempts",
            EscalationReason.REPEATED_FAILURES: f"Agent experiencing {context.get('consecutive_failures', 0)} consecutive failures",
            EscalationReason.DEPENDENCY_ISSUES: f"Multiple dependency errors preventing progress",
            EscalationReason.GOAL_DRIFT: f"Agent has drifted from project goals",
            EscalationReason.TIMEOUT_EXCEEDED: f"Task timeout exceeded ({context.get('time_spent_seconds', 0)}s)",
            EscalationReason.CRITICAL_ERROR: f"Critical system error detected",
            EscalationReason.SYSTEM_INSTABILITY: f"System instability detected"
        }
        
        return descriptions.get(reason, f"Escalation needed: {reason.value}")
    
    async def handle_escalation(self, context: EscalationContext) -> EscalationResponse:
        """
        Handle escalation based on level
        
        Args:
            context: Escalation context
            
        Returns:
            EscalationResponse with guidance and actions
        """
        
        # Store active escalation
        self.active_escalations[context.agent_id] = context
        self.escalation_history.append(context)
        
        # Trigger escalation callback
        if self.on_escalation:
            self.on_escalation(context)
        
        try:
            if context.escalation_level == EscalationLevel.LEO_INTERVENTION:
                return await self._handle_leo_intervention(context)
                
            elif context.escalation_level == EscalationLevel.OPUS_CONSULTATION:
                return await self._handle_opus_consultation(context)
                
            elif context.escalation_level == EscalationLevel.HUMAN_REQUIRED:
                return await self._handle_human_escalation(context)
                
            elif context.escalation_level == EscalationLevel.REMOTE_ACCESS:
                return await self._handle_remote_access_request(context)
                
            else:
                return EscalationResponse(
                    level=context.escalation_level,
                    success=False,
                    guidance="Unknown escalation level",
                    action_items=[],
                    estimated_resolution_time=None,
                    requires_further_escalation=True,
                    context_updates={}
                )
                
        except Exception as e:
            logger.error(f"Escalation handling failed: {e}")
            return EscalationResponse(
                level=context.escalation_level,
                success=False,
                guidance=f"Escalation system error: {str(e)}",
                action_items=["Contact system administrator"],
                estimated_resolution_time=None,
                requires_further_escalation=True,
                context_updates={}
            )
    
    async def _handle_leo_intervention(self, context: EscalationContext) -> EscalationResponse:
        """Handle LEO-level intervention"""
        
        if not self.leo_supervisor:
            return EscalationResponse(
                level=EscalationLevel.LEO_INTERVENTION,
                success=False,
                guidance="LEO supervisor not available",
                action_items=[],
                estimated_resolution_time=None,
                requires_further_escalation=True,
                context_updates={}
            )
        
        try:
            # Get LEO's analysis and guidance
            leo_context = {
                'escalation_reason': context.reason.value,
                'failed_attempts': context.failed_attempts,
                'error_messages': context.error_messages,
                'current_task': context.current_task,
                'project_goals': context.project_goals
            }
            
            guidance = self.leo_supervisor.provide_escalation_guidance(leo_context)
            
            return EscalationResponse(
                level=EscalationLevel.LEO_INTERVENTION,
                success=True,
                guidance=guidance,
                action_items=self._extract_action_items(guidance),
                estimated_resolution_time="5-15 minutes",
                requires_further_escalation=False,
                context_updates={'leo_intervention_attempted': True}
            )
            
        except Exception as e:
            logger.error(f"LEO intervention failed: {e}")
            return EscalationResponse(
                level=EscalationLevel.LEO_INTERVENTION,
                success=False,
                guidance="LEO intervention failed",
                action_items=[],
                estimated_resolution_time=None,
                requires_further_escalation=True,
                context_updates={}
            )
    
    async def _handle_opus_consultation(self, context: EscalationContext) -> EscalationResponse:
        """Handle Claude Opus consultation"""
        
        if not self.anthropic_client:
            return EscalationResponse(
                level=EscalationLevel.OPUS_CONSULTATION,
                success=False,
                guidance="Anthropic API not configured",
                action_items=["Configure Anthropic API access"],
                estimated_resolution_time=None,
                requires_further_escalation=True,
                context_updates={}
            )
        
        try:
            # Prepare detailed context for Opus
            opus_prompt = self._prepare_opus_prompt(context)
            
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": opus_prompt}]
            )
            
            guidance = response.content[0].text
            action_items = self._extract_action_items(guidance)
            
            return EscalationResponse(
                level=EscalationLevel.OPUS_CONSULTATION,
                success=True,
                guidance=guidance,
                action_items=action_items,
                estimated_resolution_time="15-30 minutes",
                requires_further_escalation=False,
                context_updates={'opus_consultation_completed': True}
            )
            
        except Exception as e:
            logger.error(f"Opus consultation failed: {e}")
            return EscalationResponse(
                level=EscalationLevel.OPUS_CONSULTATION,
                success=False,
                guidance=f"Opus consultation failed: {str(e)}",
                action_items=["Escalate to human"],
                estimated_resolution_time=None,
                requires_further_escalation=True,
                context_updates={}
            )
    
    async def _handle_human_escalation(self, context: EscalationContext) -> EscalationResponse:
        """Handle human escalation with notifications"""
        
        try:
            # Prepare human-friendly summary
            summary = self._prepare_human_summary(context)
            
            # Send notification (webhook, email, etc.)
            if self.notification_webhook:
                await self._send_webhook_notification(summary, context)
            
            # Take screenshot if possible
            screenshot_path = await self._take_screenshot()
            
            return EscalationResponse(
                level=EscalationLevel.HUMAN_REQUIRED,
                success=True,
                guidance=f"Human intervention requested. Summary: {summary}",
                action_items=[
                    "Check notification for details",
                    "Review escalation context",
                    f"Screenshot saved: {screenshot_path}" if screenshot_path else "No screenshot available"
                ],
                estimated_resolution_time="Variable - awaiting human response",
                requires_further_escalation=False,
                context_updates={
                    'human_notified': True,
                    'notification_sent_at': datetime.now().isoformat(),
                    'screenshot_path': screenshot_path
                }
            )
            
        except Exception as e:
            logger.error(f"Human escalation failed: {e}")
            return EscalationResponse(
                level=EscalationLevel.HUMAN_REQUIRED,
                success=False,
                guidance=f"Human escalation failed: {str(e)}",
                action_items=["Manual intervention required"],
                estimated_resolution_time=None,
                requires_further_escalation=False,
                context_updates={}
            )
    
    async def _handle_remote_access_request(self, context: EscalationContext) -> EscalationResponse:
        """Handle remote access escalation"""
        
        try:
            # Prepare remote access context
            access_info = {
                'escalation_id': context.agent_id,
                'timestamp': context.timestamp.isoformat(),
                'description': context.description,
                'remote_url': self.remote_access_url
            }
            
            return EscalationResponse(
                level=EscalationLevel.REMOTE_ACCESS,
                success=True,
                guidance="Remote access prepared for human intervention",
                action_items=[
                    f"Remote access URL: {self.remote_access_url}",
                    "Context preserved for remote session",
                    "System state captured"
                ],
                estimated_resolution_time="Variable - manual intervention",
                requires_further_escalation=False,
                context_updates={
                    'remote_access_prepared': True,
                    'access_info': access_info
                }
            )
            
        except Exception as e:
            logger.error(f"Remote access preparation failed: {e}")
            return EscalationResponse(
                level=EscalationLevel.REMOTE_ACCESS,
                success=False,
                guidance=f"Remote access preparation failed: {str(e)}",
                action_items=["Manual system access required"],
                estimated_resolution_time=None,
                requires_further_escalation=False,
                context_updates={}
            )
    
    def _prepare_opus_prompt(self, context: EscalationContext) -> str:
        """Prepare detailed prompt for Claude Opus"""
        return f"""
ESCALATION CONSULTATION REQUEST

Agent: {context.agent_id}
Reason: {context.reason.value}
Time: {context.timestamp}

PROBLEM DESCRIPTION:
{context.description}

CURRENT TASK:
{context.current_task or 'None specified'}

FAILED ATTEMPTS: {context.failed_attempts}

RECENT ERROR MESSAGES:
{chr(10).join(context.error_messages[-5:]) if context.error_messages else 'None'}

RECENT COMMANDS:
{chr(10).join(context.recent_commands[-5:]) if context.recent_commands else 'None'}

PROJECT GOALS:
{chr(10).join(context.project_goals) if context.project_goals else 'None specified'}

PREVIOUS ESCALATIONS:
{chr(10).join(context.previous_escalations) if context.previous_escalations else 'None'}

TIME SPENT: {context.time_spent}
COMPLETION: {context.completion_percentage}%

Please provide:
1. Root cause analysis
2. Specific step-by-step resolution guidance
3. Prevention strategies for similar issues
4. Estimated resolution time
5. Whether further escalation is needed

Focus on actionable, technical guidance that can get development back on track.
"""
    
    def _prepare_human_summary(self, context: EscalationContext) -> str:
        """Prepare human-friendly escalation summary"""
        return f"""
LeoDock Escalation Alert

Agent {context.agent_id} needs assistance:
- Reason: {context.reason.value}
- Task: {context.current_task or 'Unknown'}
- Duration: {context.time_spent}
- Failed attempts: {context.failed_attempts}

Latest error: {context.error_messages[-1] if context.error_messages else 'None'}

Action required: Review and provide guidance
"""
    
    async def _send_webhook_notification(self, summary: str, context: EscalationContext):
        """Send webhook notification to user"""
        import aiohttp
        
        if not self.notification_webhook:
            return
            
        payload = {
            'type': 'escalation',
            'summary': summary,
            'context': context.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.notification_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("Webhook notification sent successfully")
                    else:
                        logger.warning(f"Webhook notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")
    
    async def _take_screenshot(self) -> Optional[str]:
        """Take system screenshot for escalation"""
        try:
            from PIL import ImageGrab
            import tempfile
            
            screenshot = ImageGrab.grab()
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                screenshot.save(f.name)
                return f.name
                
        except ImportError:
            logger.warning("PIL not available for screenshots")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
        
        return None
    
    def _extract_action_items(self, guidance: str) -> List[str]:
        """Extract actionable items from guidance text"""
        lines = guidance.split('\n')
        action_items = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                action_items.append(line)
            elif line.startswith(('Action:', 'TODO:', 'Next:')):
                action_items.append(line)
        
        return action_items[:10]  # Limit to 10 items
    
    def _get_previous_escalations(self, agent_id: str) -> List[str]:
        """Get previous escalations for agent"""
        previous = []
        for escalation in self.escalation_history:
            if escalation.agent_id == agent_id:
                previous.append(f"{escalation.timestamp}: {escalation.reason.value}")
        
        return previous[-5:]  # Last 5 escalations
    
    def _has_recent_escalations(self, agent_id: str) -> bool:
        """Check if agent has recent escalations"""
        cutoff = datetime.now() - timedelta(hours=1)
        
        for escalation in self.escalation_history:
            if (escalation.agent_id == agent_id and 
                escalation.timestamp > cutoff):
                return True
        
        return False
    
    def resolve_escalation(self, agent_id: str, resolution_notes: str):
        """Mark escalation as resolved"""
        if agent_id in self.active_escalations:
            context = self.active_escalations[agent_id]
            context.resolution_attempts.append(f"{datetime.now()}: {resolution_notes}")
            
            del self.active_escalations[agent_id]
            
            if self.on_resolution:
                self.on_resolution(context, resolution_notes)
    
    def get_escalation_stats(self) -> Dict[str, Any]:
        """Get escalation system statistics"""
        return {
            'active_escalations': len(self.active_escalations),
            'total_escalations': len(self.escalation_history),
            'escalation_reasons': {
                reason.value: sum(1 for e in self.escalation_history if e.reason == reason)
                for reason in EscalationReason
            },
            'escalation_levels': {
                level.value: sum(1 for e in self.escalation_history if e.escalation_level == level)
                for level in EscalationLevel
            },
            'recent_escalations': len([
                e for e in self.escalation_history 
                if e.timestamp > datetime.now() - timedelta(hours=24)
            ])
        }