"""
LEO Dashboard - Make LEO's thoughts and actions visible to the user
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LEOActivityLogger:
    """
    Logs LEO activity in plain English for user visibility
    """
    
    def __init__(self, log_file: str = "data/leo_activity.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # In-memory activity for web dashboard
        self.recent_activities: List[Dict[str, Any]] = []
        self.max_activities = 100
        
    def log_activity(self, 
                    activity_type: str,
                    description: str, 
                    details: Dict[str, Any] = None,
                    importance: str = "normal"):
        """
        Log LEO activity in plain English
        
        Args:
            activity_type: Type of activity (monitoring, guidance, escalation, etc.)
            description: Plain English description
            details: Technical details (optional)
            importance: low, normal, high, critical
        """
        
        timestamp = datetime.now()
        
        activity = {
            "timestamp": timestamp.isoformat(),
            "time_friendly": timestamp.strftime("%H:%M:%S"),
            "type": activity_type,
            "description": description,
            "details": details or {},
            "importance": importance
        }
        
        # Add to recent activities
        self.recent_activities.append(activity)
        
        # Keep only recent activities
        if len(self.recent_activities) > self.max_activities:
            self.recent_activities = self.recent_activities[-self.max_activities:]
        
        # Log to file
        self._write_to_file(activity)
        
        # Print to console for immediate visibility
        self._print_activity(activity)
    
    def _write_to_file(self, activity: Dict[str, Any]):
        """Write activity to log file"""
        try:
            with open(self.log_file, "a") as f:
                f.write(f"{activity['timestamp']} [{activity['importance'].upper()}] {activity['type']}: {activity['description']}\n")
                if activity['details']:
                    f.write(f"  Details: {json.dumps(activity['details'], indent=2)}\n")
                f.write("\n")
        except Exception as e:
            logger.error(f"Failed to write LEO activity to file: {e}")
    
    def _print_activity(self, activity: Dict[str, Any]):
        """Print activity to console for immediate visibility"""
        
        # Color coding for importance
        colors = {
            "low": "\033[37m",      # Light gray
            "normal": "\033[36m",   # Cyan  
            "high": "\033[33m",     # Yellow
            "critical": "\033[31m"  # Red
        }
        reset = "\033[0m"
        
        color = colors.get(activity['importance'], colors['normal'])
        
        print(f"{color}🤖 LEO [{activity['time_friendly']}]: {activity['description']}{reset}")
        
        if activity['details'] and activity['importance'] in ['high', 'critical']:
            print(f"   Details: {activity['details']}")
    
    def get_recent_activities(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activities for web dashboard"""
        return self.recent_activities[-limit:]
    
    def get_activities_by_type(self, activity_type: str) -> List[Dict[str, Any]]:
        """Get activities filtered by type"""
        return [a for a in self.recent_activities if a['type'] == activity_type]
    
    def clear_activities(self):
        """Clear activity log"""
        self.recent_activities = []
        try:
            self.log_file.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Failed to clear activity log: {e}")


class LEOStatusTracker:
    """
    Track LEO's current status and decision making
    """
    
    def __init__(self):
        self.current_status = "idle"
        self.current_task = None
        self.current_reasoning = ""
        self.decisions_made = []
        self.performance_metrics = {
            "interactions_monitored": 0,
            "interventions_made": 0,
            "escalations_triggered": 0,
            "autonomous_tasks_completed": 0
        }
    
    def update_status(self, status: str, task: str = None, reasoning: str = ""):
        """Update LEO's current status"""
        self.current_status = status
        self.current_task = task
        self.current_reasoning = reasoning
        
        logger.info(f"LEO Status: {status} | Task: {task} | Reasoning: {reasoning}")
    
    def record_decision(self, decision: str, reasoning: str, outcome: str = None):
        """Record a decision made by LEO"""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "reasoning": reasoning,
            "outcome": outcome
        }
        
        self.decisions_made.append(decision_record)
        
        # Keep only recent decisions
        if len(self.decisions_made) > 50:
            self.decisions_made = self.decisions_made[-50:]
    
    def increment_metric(self, metric: str):
        """Increment a performance metric"""
        if metric in self.performance_metrics:
            self.performance_metrics[metric] += 1
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current status summary"""
        return {
            "status": self.current_status,
            "current_task": self.current_task,
            "reasoning": self.current_reasoning,
            "recent_decisions": self.decisions_made[-5:],
            "performance": self.performance_metrics,
            "uptime": str(datetime.now() - datetime.now())  # Will be properly calculated
        }


# Global instances
leo_activity = LEOActivityLogger()
leo_status = LEOStatusTracker()


def log_leo_thought(thought: str, details: Dict = None, importance: str = "normal"):
    """Helper function to log LEO's thoughts"""
    leo_activity.log_activity("thinking", f"LEO is thinking: {thought}", details, importance)


def log_leo_decision(decision: str, reasoning: str, importance: str = "normal"):
    """Helper function to log LEO's decisions"""
    leo_activity.log_activity("decision", f"LEO decided: {decision}", {"reasoning": reasoning}, importance)
    leo_status.record_decision(decision, reasoning)


def log_leo_monitoring(agent: str, action: str, result: str):
    """Helper function to log LEO's monitoring activities"""
    leo_activity.log_activity("monitoring", f"LEO monitored {agent}: {action} → {result}")
    leo_status.increment_metric("interactions_monitored")


def log_leo_intervention(intervention: str, reason: str):
    """Helper function to log LEO's interventions"""
    leo_activity.log_activity("intervention", f"LEO intervened: {intervention}", {"reason": reason}, "high")
    leo_status.increment_metric("interventions_made")


def log_leo_escalation(escalation_type: str, reason: str):
    """Helper function to log LEO's escalations"""
    leo_activity.log_activity("escalation", f"LEO escalated to {escalation_type}: {reason}", importance="critical")
    leo_status.increment_metric("escalations_triggered")


def log_leo_success(achievement: str, details: Dict = None):
    """Helper function to log LEO's successes"""
    leo_activity.log_activity("success", f"LEO achieved: {achievement}", details, "normal")
    leo_status.increment_metric("autonomous_tasks_completed")