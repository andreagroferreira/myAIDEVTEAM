"""
Task Coordinator for CFTeam ecosystem
Coordinates task execution across agents and crews
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import uuid

from src.config import get_logger, RedisCache, RedisPubSub, CHANNELS
from src.models import Task, TaskStatus, TaskPriority, TaskType


class TaskCoordinator:
    """Coordinates task execution"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = RedisCache(prefix="task:")
        self.pubsub = RedisPubSub()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Task] = {}
    
    async def initialize(self):
        """Initialize task coordinator"""
        # Subscribe to task channels
        await self.pubsub.subscribe([
            CHANNELS['task_updates'],
            CHANNELS['crew_coordination']
        ])
        
        self.logger.info("Task coordinator initialized")
    
    async def shutdown(self):
        """Shutdown task coordinator"""
        # Unsubscribe from channels
        await self.pubsub.unsubscribe()
        await self.pubsub.close()
        
        self.logger.info("Task coordinator shutting down")
    
    async def create_task(
        self,
        session_id: str,
        title: str,
        description: Optional[str] = None,
        task_type: TaskType = TaskType.DEVELOPMENT,
        priority: TaskPriority = TaskPriority.MEDIUM,
        project: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        requirements: Optional[List[str]] = None,
        assigned_crew: Optional[str] = None
    ) -> Task:
        """Create a new task"""
        task = Task(
            session_id=uuid.UUID(session_id),
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            project=project or "default",
            dependencies=dependencies or [],
            requirements=requirements or [],
            assigned_crew=assigned_crew
        )
        
        # Save to database
        # TODO: Implement database save
        
        # Cache task
        await self.cache.set(str(task.id), task.to_dict())
        self.active_tasks[str(task.id)] = task
        
        # Add to queue if no dependencies
        if not task.dependencies:
            await self.task_queue.put(task)
        
        # Publish task created event
        await self.pubsub.publish(CHANNELS['task_updates'], {
            "type": "task_created",
            "task_id": str(task.id),
            "session_id": session_id,
            "priority": priority.value
        })
        
        self.logger.info(f"Created task: {task.title} ({task.id})")
        return task
    
    async def assign_task(self, task_id: str, agent_id: str, crew_name: str):
        """Assign task to an agent"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        task.assign_to(agent_id, crew_name)
        await self.update_task(task)
        
        # Notify agent
        await self.pubsub.publish(f"agent:{agent_id}:commands", {
            "type": "task_assignment",
            "task": task.to_dict()
        })
        
        self.logger.info(f"Assigned task {task_id} to agent {agent_id}")
        return True
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check cache
        cached = await self.cache.get(task_id)
        if cached:
            # TODO: Reconstruct Task from dict
            pass
        
        # Load from database
        # TODO: Implement database load
        
        return None
    
    async def update_task(self, task: Task):
        """Update task"""
        # Update cache
        await self.cache.set(str(task.id), task.to_dict())
        
        # Update database
        # TODO: Implement database update
        
        # Publish update event
        await self.pubsub.publish(CHANNELS['task_updates'], {
            "type": "task_updated",
            "task_id": str(task.id),
            "status": task.status.value
        })
    
    async def get_next_task(self, capabilities: List[str]) -> Optional[Task]:
        """Get next available task matching capabilities"""
        try:
            # Get task from queue (non-blocking)
            task = self.task_queue.get_nowait()
            
            # TODO: Check if task matches agent capabilities
            
            return task
        except asyncio.QueueEmpty:
            return None
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        task.complete(result)
        await self.update_task(task)
        
        # Remove from active tasks
        self.active_tasks.pop(task_id, None)
        
        # Check for dependent tasks
        await self._process_dependent_tasks(task_id)
        
        self.logger.info(f"Completed task: {task.title} ({task_id})")
        return True
    
    async def _process_dependent_tasks(self, completed_task_id: str):
        """Process tasks that depend on the completed task"""
        # TODO: Find tasks with this dependency and check if they're ready
        pass