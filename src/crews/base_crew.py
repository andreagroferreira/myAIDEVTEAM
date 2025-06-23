"""
Base Crew class for CFTeam ecosystem
Manages groups of agents working together
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
import asyncio
from enum import Enum

from crewai import Crew as CrewAICrew, Process
from pydantic import BaseModel, Field

from src.config import get_logger, RedisCache, RedisPubSub, CHANNELS
from src.agents.base_agent import BaseAgent
from src.models import Task, TaskStatus, Session


class CrewProcess(Enum):
    """Crew process types"""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    PARALLEL = "parallel"


class CrewConfig(BaseModel):
    """Crew configuration schema"""
    name: str
    description: str
    agents: List[str]  # Agent identifiers
    process: CrewProcess = CrewProcess.SEQUENTIAL
    manager_agent: Optional[str] = None  # For hierarchical process
    verbose: bool = True
    memory: bool = True
    planning: bool = False
    max_iterations: int = 10
    responsibilities: List[str] = Field(default_factory=list)


class BaseCrew(ABC):
    """Base class for all crews"""
    
    def __init__(self, config: CrewConfig):
        self.config = config
        self.logger = get_logger(f"crew.{config.name.lower().replace(' ', '_')}")
        
        # CrewAI crew instance
        self._crewai_crew: Optional[CrewAICrew] = None
        
        # Agent instances
        self.agents: Dict[str, BaseAgent] = {}
        self.manager: Optional[BaseAgent] = None
        
        # Communication
        self.cache = RedisCache(prefix=f"crew:{config.name}:")
        self.pubsub = RedisPubSub()
        
        # State
        self.is_initialized = False
        self.current_session: Optional[Session] = None
        self.active_tasks: List[Task] = []
        
        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.start_time: Optional[datetime] = None
    
    @abstractmethod
    async def initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize and return crew agents - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def define_tasks(self, objective: str) -> List[Any]:
        """Define tasks for the crew - must be implemented by subclasses"""
        pass
    
    async def initialize(self):
        """Initialize the crew"""
        try:
            self.logger.info(f"Initializing {self.config.name} crew...")
            
            # Initialize agents
            self.agents = await self.initialize_agents()
            
            # Set up manager for hierarchical process
            if self.config.process == CrewProcess.HIERARCHICAL:
                if not self.config.manager_agent:
                    raise ValueError("Hierarchical process requires a manager agent")
                
                self.manager = self.agents.get(self.config.manager_agent)
                if not self.manager:
                    raise ValueError(f"Manager agent {self.config.manager_agent} not found")
            
            # Initialize all agents
            for agent_id, agent in self.agents.items():
                await agent.setup()
                self.logger.info(f"Initialized agent: {agent_id}")
            
            # Create CrewAI crew
            self._create_crewai_crew()
            
            # Subscribe to crew channels
            await self.pubsub.subscribe([
                CHANNELS['crew_coordination'],
                f"crew:{self.config.name}:commands",
                f"crew:{self.config.name}:reports"
            ])
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            self.is_initialized = True
            self.start_time = datetime.utcnow()
            
            self.logger.info(f"{self.config.name} crew initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crew: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """Shutdown the crew"""
        try:
            self.logger.info(f"Shutting down {self.config.name} crew...")
            
            # Shutdown all agents
            shutdown_tasks = []
            for agent_id, agent in self.agents.items():
                shutdown_tasks.append(agent.shutdown())
            
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            # Unsubscribe from channels
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            
            self.logger.info(f"{self.config.name} crew shut down")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def execute_objective(self, objective: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a crew objective"""
        self.logger.info(f"Executing objective: {objective}")
        
        try:
            # Define tasks for the objective
            tasks = await self.define_tasks(objective)
            
            # Get CrewAI crew
            if not self._crewai_crew:
                raise RuntimeError("CrewAI crew not initialized")
            
            # Set context if provided
            if context:
                # Pass context to agents
                for agent in self.agents.values():
                    agent.current_session_id = context.get("session_id")
            
            # Execute with CrewAI
            result = self._crewai_crew.kickoff(
                tasks=tasks,
                inputs={"objective": objective, "context": context or {}}
            )
            
            # Process and return result
            return self._process_crew_result(result)
            
        except Exception as e:
            self.logger.error(f"Failed to execute objective: {e}", exc_info=True)
            self.tasks_failed += 1
            raise
    
    async def assign_task(self, task: Task) -> bool:
        """Assign a task to the crew"""
        try:
            # Find best agent for the task
            agent = await self._select_agent_for_task(task)
            if not agent:
                self.logger.warning(f"No suitable agent found for task: {task.title}")
                return False
            
            # Add to active tasks
            self.active_tasks.append(task)
            
            # Execute task
            asyncio.create_task(self._execute_agent_task(agent, task))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}", exc_info=True)
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get crew status"""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = {
                "status": await agent.cache.get("status") or "unknown",
                "current_task": str(agent.current_task.id) if agent.current_task else None,
                "tasks_completed": agent.tasks_succeeded,
                "tasks_failed": agent.tasks_failed
            }
        
        return {
            "crew": self.config.name,
            "status": "active" if self.is_initialized else "inactive",
            "agents": agent_statuses,
            "active_tasks": len(self.active_tasks),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def _create_crewai_crew(self):
        """Create CrewAI crew instance"""
        # Map our process enum to CrewAI process
        process_map = {
            CrewProcess.SEQUENTIAL: Process.sequential,
            CrewProcess.HIERARCHICAL: Process.hierarchical,
            CrewProcess.PARALLEL: Process.sequential  # CrewAI doesn't have parallel yet
        }
        
        # Get CrewAI agents
        crewai_agents = [agent.get_crewai_agent() for agent in self.agents.values()]
        
        # Create crew
        crew_kwargs = {
            "agents": crewai_agents,
            "process": process_map[self.config.process],
            "verbose": self.config.verbose,
            "memory": self.config.memory,
            "planning": self.config.planning,
            "max_iter": self.config.max_iterations,
        }
        
        # Add manager for hierarchical process
        if self.config.process == CrewProcess.HIERARCHICAL and self.manager:
            crew_kwargs["manager_agent"] = self.manager.get_crewai_agent()
        
        self._crewai_crew = CrewAICrew(**crew_kwargs)
    
    async def _listen_for_messages(self):
        """Listen for crew messages"""
        try:
            async for message in self.pubsub.listen():
                await self._handle_message(message)
        except Exception as e:
            self.logger.error(f"Error in message listener: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages"""
        try:
            msg_type = message.get("data", {}).get("type")
            
            if msg_type == "task_assignment":
                task_data = message["data"].get("task")
                # TODO: Reconstruct task and assign
                
            elif msg_type == "status_request":
                status = await self.get_status()
                await self._publish_status(status)
                
            elif msg_type == "objective":
                objective = message["data"].get("objective")
                context = message["data"].get("context")
                asyncio.create_task(self.execute_objective(objective, context))
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def _select_agent_for_task(self, task: Task) -> Optional[BaseAgent]:
        """Select best agent for a task"""
        # Simple selection based on availability
        for agent in self.agents.values():
            if await agent.cache.get("status") == "available":
                return agent
        
        # TODO: Implement smarter selection based on capabilities
        return None
    
    async def _execute_agent_task(self, agent: BaseAgent, task: Task):
        """Execute task with agent"""
        try:
            result = await agent.execute_task(task)
            
            # Update metrics
            self.tasks_completed += 1
            
            # Remove from active tasks
            self.active_tasks.remove(task)
            
            # Report completion
            await self._report_task_completion(task, result)
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.tasks_failed += 1
            
            # Remove from active tasks
            if task in self.active_tasks:
                self.active_tasks.remove(task)
    
    async def _report_task_completion(self, task: Task, result: Dict[str, Any]):
        """Report task completion"""
        await self.pubsub.publish(CHANNELS['task_updates'], {
            "type": "task_completed_by_crew",
            "crew": self.config.name,
            "task_id": str(task.id),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _publish_status(self, status: Dict[str, Any]):
        """Publish crew status"""
        await self.pubsub.publish(CHANNELS['system_events'], {
            "type": "crew_status",
            "source": f"crew:{self.config.name}",
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _process_crew_result(self, result: Any) -> Dict[str, Any]:
        """Process result from CrewAI execution"""
        return {
            "status": "completed",
            "crew": self.config.name,
            "result": str(result),  # CrewAI returns various types
            "timestamp": datetime.utcnow().isoformat(),
            "tasks_completed": self.tasks_completed
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.config.name}', agents={len(self.agents)})>"