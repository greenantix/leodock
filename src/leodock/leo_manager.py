"""
LEO Manager - Central coordination for LEO supervisor system
Handles initialization, configuration, and switching between real/mock LEO
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv
from pathlib import Path

from .leo_supervisor import LEOSupervisor
from .mock_leo_supervisor import MockLEOSupervisor
from .agent_interface import AgentInterface, AgentType, claude_code_interface
# Context indexer is optional - import only if available
try:
    from .context_indexer import ContextIndexer
    CONTEXT_INDEXER_AVAILABLE = True
except ImportError:
    ContextIndexer = None
    CONTEXT_INDEXER_AVAILABLE = False
from .escalation_system import EscalationSystem

logger = logging.getLogger(__name__)


class LEOManager:
    """
    Central manager for LEO supervisor system
    Coordinates all LEO components and provides unified interface
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or ".env"
        self.config = self._load_config()
        
        # Core components
        self.leo_supervisor: Optional[Union[LEOSupervisor, MockLEOSupervisor]] = None
        self.context_indexer: Optional[ContextIndexer] = None
        self.escalation_system: Optional[EscalationSystem] = None
        self.agent_interfaces: Dict[str, AgentInterface] = {}
        
        # State
        self.is_initialized = False
        self.mock_mode = self.config.get('MOCK_LEO_SUPERVISOR', 'true').lower() == 'true'
        
        logger.info(f"🎯 LEO Manager initialized (mock_mode: {self.mock_mode})")
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from environment and .env file"""
        
        # Load .env file if it exists
        env_path = Path(self.config_path)
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"📁 Loaded config from {env_path}")
        
        # Return all environment variables as config
        return dict(os.environ)
    
    def initialize(self) -> bool:
        """
        Initialize all LEO components
        
        Returns:
            bool: True if initialization successful
        """
        
        if self.is_initialized:
            logger.warning("LEO Manager already initialized")
            return True
        
        try:
            logger.info("🚀 Initializing LEO system components...")
            
            # Initialize LEO supervisor
            if not self._init_leo_supervisor():
                logger.error("Failed to initialize LEO supervisor")
                return False
            
            # Initialize context indexer
            if not self._init_context_indexer():
                logger.error("Failed to initialize context indexer")
                return False
            
            # Initialize escalation system
            if not self._init_escalation_system():
                logger.error("Failed to initialize escalation system")
                return False
            
            # Initialize agent interfaces
            if not self._init_agent_interfaces():
                logger.error("Failed to initialize agent interfaces")
                return False
            
            # Connect components
            self._connect_components()
            
            self.is_initialized = True
            logger.info("✅ LEO system fully initialized!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ LEO initialization failed: {e}")
            return False
    
    def _init_leo_supervisor(self) -> bool:
        """Initialize LEO supervisor (real or mock)"""
        
        try:
            if self.mock_mode:
                logger.info("🤖 Starting Mock LEO Supervisor...")
                self.leo_supervisor = MockLEOSupervisor(
                    model_name="mock-llama-3.1-8b",
                    anthropic_api_key=self.config.get('ANTHROPIC_API_KEY')
                )
            else:
                logger.info("🧠 Starting Real LEO Supervisor...")
                self.leo_supervisor = LEOSupervisor(
                    model_name=self.config.get('LM_STUDIO_MODEL', 'llama-3.1-8b'),
                    anthropic_api_key=self.config.get('ANTHROPIC_API_KEY')
                )
            
            logger.info("✅ LEO supervisor initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ LEO supervisor initialization failed: {e}")
            return False
    
    def _init_context_indexer(self) -> bool:
        """Initialize context indexer for semantic search"""
        
        if not CONTEXT_INDEXER_AVAILABLE:
            logger.info("⚠️  Context indexer dependencies not available - skipping")
            return True
        
        try:
            db_path = self.config.get('CONTEXT_DB_PATH', './data/context_db')
            
            self.context_indexer = ContextIndexer(
                db_path=db_path,
                embedding_model="all-MiniLM-L6-v2"
            )
            
            logger.info("✅ Context indexer initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Context indexer initialization failed: {e}")
            # Continue without context indexer for now
            return True
    
    def _init_escalation_system(self) -> bool:
        """Initialize escalation system"""
        
        try:
            # Import here to avoid circular dependencies
            from anthropic import Anthropic
            
            anthropic_client = None
            if self.config.get('ANTHROPIC_API_KEY'):
                anthropic_client = Anthropic(api_key=self.config.get('ANTHROPIC_API_KEY'))
            
            self.escalation_system = EscalationSystem(
                leo_supervisor=self.leo_supervisor,
                anthropic_client=anthropic_client,
                notification_webhook=self.config.get('ESCALATION_WEBHOOK_URL'),
                remote_access_url=self.config.get('REMOTE_ACCESS_URL')
            )
            
            logger.info("✅ Escalation system initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Escalation system initialization failed: {e}")
            # Continue without escalation system for now
            return True
    
    def _init_agent_interfaces(self) -> bool:
        """Initialize agent interfaces"""
        
        try:
            # Initialize Claude Code interface
            claude_code_interface.set_leo_supervisor(self.leo_supervisor)
            self.agent_interfaces['claude_code'] = claude_code_interface
            
            # Set up callbacks
            claude_code_interface.on_guidance_received = self._handle_guidance
            claude_code_interface.on_escalation = self._handle_escalation
            claude_code_interface.on_task_updated = self._handle_task_update
            
            logger.info("✅ Agent interfaces initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent interface initialization failed: {e}")
            return False
    
    def _connect_components(self):
        """Connect all components together"""
        
        # Connect escalation system to LEO supervisor
        if self.escalation_system and self.leo_supervisor:
            self.escalation_system.leo_supervisor = self.leo_supervisor
        
        logger.info("🔗 Components connected")
    
    def _handle_guidance(self, guidance: str, analysis: Dict[str, Any]):
        """Handle guidance from LEO"""
        logger.info(f"🎯 LEO Guidance: {guidance}")
        
        # Could trigger notifications, logging, etc.
        if analysis.get('priority') == 'high':
            logger.warning(f"🚨 High priority guidance: {guidance}")
    
    def _handle_escalation(self, opus_response: str, context: Dict[str, Any]):
        """Handle escalation response"""
        logger.warning(f"🆘 Escalation Response: {opus_response}")
        
        # Could trigger notifications, save to file, etc.
    
    def _handle_task_update(self, task):
        """Handle task updates"""
        logger.info(f"📋 Task Update: {task.description} -> {task.status.value}")
    
    def get_claude_interface(self) -> AgentInterface:
        """Get Claude Code agent interface"""
        return self.agent_interfaces.get('claude_code', claude_code_interface)
    
    def monitor_claude_interaction(self, 
                                 command: str,
                                 output: str,
                                 files_modified: list = None,
                                 success: bool = True,
                                 context: dict = None) -> str:
        """
        Monitor Claude Code interaction through LEO
        
        Returns:
            interaction_id for tracking
        """
        
        if not self.is_initialized:
            logger.warning("LEO Manager not initialized - skipping monitoring")
            return "unmonitored"
        
        interface = self.get_claude_interface()
        return interface.register_interaction(
            command=command,
            output=output,
            files_modified=files_modified or [],
            success=success,
            context=context or {}
        )
    
    def generate_claude_md(self) -> Optional[str]:
        """Generate CLAUDE.md file for next development phase"""
        
        if not self.leo_supervisor:
            return None
        
        interface = self.get_claude_interface()
        return interface.request_claude_md_generation()
    
    def index_project(self, project_path: str = ".") -> Dict[str, Any]:
        """Index project for context search"""
        
        if not self.context_indexer:
            return {"error": "Context indexer not available"}
        
        return self.context_indexer.index_project(project_path)
    
    def search_context(self, query: str, n_results: int = 5) -> list:
        """Search project context"""
        
        if not self.context_indexer:
            return []
        
        return self.context_indexer.search_context(query, n_results)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        
        status = {
            "leo_manager": {
                "initialized": self.is_initialized,
                "mock_mode": self.mock_mode,
                "config_loaded": bool(self.config)
            },
            "leo_supervisor": {
                "available": self.leo_supervisor is not None,
                "type": "mock" if self.mock_mode else "real",
                "model": self.config.get('LM_STUDIO_MODEL', 'unknown')
            },
            "context_indexer": {
                "available": self.context_indexer is not None,
                "db_path": self.config.get('CONTEXT_DB_PATH', 'unknown')
            },
            "escalation_system": {
                "available": self.escalation_system is not None,
                "anthropic_configured": bool(self.config.get('ANTHROPIC_API_KEY')),
                "webhook_configured": bool(self.config.get('ESCALATION_WEBHOOK_URL'))
            },
            "agent_interfaces": {
                "count": len(self.agent_interfaces),
                "claude_code": "claude_code" in self.agent_interfaces
            }
        }
        
        # Add LEO supervisor session info if available
        if self.leo_supervisor:
            try:
                status["leo_supervisor"]["session"] = self.leo_supervisor.get_session_summary()
            except:
                pass
        
        return status
    
    def shutdown(self):
        """Shutdown LEO system gracefully"""
        
        logger.info("🛑 Shutting down LEO system...")
        
        # Could save state, close connections, etc.
        
        self.is_initialized = False
        logger.info("✅ LEO system shutdown complete")


# Global LEO manager instance
leo_manager = LEOManager()