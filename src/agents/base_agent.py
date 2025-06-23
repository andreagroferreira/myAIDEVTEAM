"""
Base Agent class for CFTeam ecosystem
Provides common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Type
from datetime import datetime
import asyncio
import uuid
import logging
from crewai import Agent as CrewAIAgent
from pydantic import BaseModel, Field

from src.config.redis_config import RedisCache, RedisPubSub, CHANNELS
from src.models.agent import Agent as AgentModel, AgentStatus, AgentRole, AgentTier
from src.models.task import Task, TaskStatus


class AgentConfig(BaseModel):
    """Agent configuration schema"""
    identifier: str
    name: str
    role: AgentRole
    tier: AgentTier
    goal: str
    backstory: str
    capabilities: List[str] = Field(default_factory=list)
    tools: List[Any] = Field(default_factory=list)
    max_rpm: int = 20
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 3
    allow_delegation: bool = False
    can_manage_crew: bool = False
    verbose: bool = True


class BaseAgent(ABC):
    """Base class for all CFTeam agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"agent.{config.identifier}")
        
        # CrewAI agent instance
        self._crewai_agent: Optional[CrewAIAgent] = None
        
        # Communication
        self.cache = RedisCache(prefix=f"agent:{config.identifier}:")
        self.pubsub = RedisPubSub()
        
        # State
        self.current_task: Optional[Task] = None
        self.current_session_id: Optional[str] = None
        self.is_initialized = False
        
        # Metrics
        self.start_time: Optional[datetime] = None
        self.tasks_processed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        
    @abstractmethod
    async def initialize(self):
        """Initialize the agent - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass
    
    async def setup(self):
        """Common setup for all agents"""
        try:
            # Initialize CrewAI agent
            self._crewai_agent = CrewAIAgent(
                role=self.config.name,
                goal=self.config.goal,
                backstory=self.config.backstory,
                tools=self.config.tools,
                verbose=self.config.verbose,
                allow_delegation=self.config.allow_delegation,
                max_iter=self.config.retry_attempts,
            )
            
            # Subscribe to relevant channels
            await self.pubsub.subscribe([
                CHANNELS['agent_communication'],
                CHANNELS['task_updates'],
                f"agent:{self.config.identifier}:commands"
            ])
            
            # Register agent in database
            await self._register_agent()
            
            # Call subclass initialization
            await self.initialize()
            
            self.is_initialized = True
            self.start_time = datetime.utcnow()
            self.logger.info(f"Agent {self.config.identifier} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the agent"""
        try:
            # Update agent status
            await self._update_status(AgentStatus.OFFLINE)
            
            # Unsubscribe from channels
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            
            # Clear cache
            await self.cache.delete("status")
            
            self.logger.info(f"Agent {self.config.identifier} shut down")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task with error handling and metrics"""
        self.current_task = task
        self.tasks_processed += 1
        
        try:
            # Update status
            await self._update_status(AgentStatus.BUSY)
            
            # Start task
            task.start()
            task.assigned_agent = self.config.identifier
            
            # Notify task start
            await self._publish_event("task_started", {
                "task_id": str(task.id),
                "agent_id": self.config.identifier,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Process task (implemented by subclass)
            start_time = datetime.utcnow()
            result = await asyncio.wait_for(
                self.process_task(task),
                timeout=self.config.timeout_seconds
            )
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Task succeeded
            task.complete(result)
            self.tasks_succeeded += 1
            
            # Update metrics
            await self._record_task_metrics(execution_time, success=True)
            
            # Notify task completion
            await self._publish_event("task_completed", {
                "task_id": str(task.id),
                "agent_id": self.config.identifier,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Task {task.id} timed out after {self.config.timeout_seconds} seconds"
            self.logger.error(error_msg)
            task.fail(error_msg)
            self.tasks_failed += 1
            await self._record_task_metrics(self.config.timeout_seconds, success=False)
            raise
            
        except Exception as e:
            error_msg = f"Task {task.id} failed: {str(e)}"
            self.logger.error(error_msg)
            task.fail(error_msg)
            self.tasks_failed += 1
            
            # Notify task failure
            await self._publish_event("task_failed", {
                "task_id": str(task.id),
                "agent_id": self.config.identifier,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            raise
            
        finally:
            self.current_task = None
            await self._update_status(AgentStatus.AVAILABLE)
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages"""
        msg_type = message.get("type")
        
        if msg_type == "ping":
            await self._handle_ping()
        elif msg_type == "status_request":
            await self._handle_status_request()
        elif msg_type == "task_assignment":
            await self._handle_task_assignment(message.get("task"))
        elif msg_type == "shutdown":
            await self.shutdown()
        else:
            # Let subclasses handle custom messages
            await self.handle_custom_message(message)
    
    async def handle_custom_message(self, message: Dict[str, Any]):
        """Override in subclasses to handle custom messages"""
        pass
    
    def get_crewai_agent(self) -> CrewAIAgent:
        """Get the underlying CrewAI agent"""
        if not self._crewai_agent:
            raise RuntimeError("Agent not initialized")
        return self._crewai_agent
    
    async def collaborate_with(self, other_agent_id: str, message: Dict[str, Any]):
        """Send a message to another agent"""
        await self.pubsub.publish(
            f"agent:{other_agent_id}:commands",
            {
                "from": self.config.identifier,
                "to": other_agent_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def report_to_crew(self, crew_name: str, report: Dict[str, Any]):
        """Report to a crew"""
        await self.pubsub.publish(
            f"crew:{crew_name}:reports",
            {
                "agent_id": self.config.identifier,
                "report": report,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Private helper methods
    
    async def _register_agent(self):
        """Register agent in database"""
        # This would create/update the agent record in the database
        pass
    
    async def _update_status(self, status: AgentStatus):
        """Update agent status"""
        await self.cache.set("status", status.value)
        await self._publish_event("status_changed", {
            "agent_id": self.config.identifier,
            "status": status.value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish an event"""
        await self.pubsub.publish(CHANNELS['system_events'], {
            "type": event_type,
            "source": f"agent:{self.config.identifier}",
            "data": data
        })
    
    async def _record_task_metrics(self, execution_time: float, success: bool):
        """Record task execution metrics"""
        metrics = {
            "tasks_processed": self.tasks_processed,
            "tasks_succeeded": self.tasks_succeeded,
            "tasks_failed": self.tasks_failed,
            "success_rate": (self.tasks_succeeded / self.tasks_processed) * 100 if self.tasks_processed > 0 else 0,
            "last_execution_time": execution_time,
            "last_execution_success": success,
            "updated_at": datetime.utcnow().isoformat()
        }
        await self.cache.set("metrics", metrics)
    
    async def _handle_ping(self):
        """Handle ping request"""
        await self._publish_event("pong", {
            "agent_id": self.config.identifier,
            "status": await self.cache.get("status") or "unknown",
            "uptime": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        })
    
    async def _handle_status_request(self):
        """Handle status request"""
        metrics = await self.cache.get("metrics") or {}
        await self._publish_event("status_response", {
            "agent_id": self.config.identifier,
            "status": await self.cache.get("status") or "unknown",
            "current_task": str(self.current_task.id) if self.current_task else None,
            "metrics": metrics
        })
    
    async def _handle_task_assignment(self, task_data: Dict[str, Any]):
        """Handle task assignment"""
        # This would be implemented to handle incoming task assignments
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.config.identifier}, role={self.config.role.value})>"