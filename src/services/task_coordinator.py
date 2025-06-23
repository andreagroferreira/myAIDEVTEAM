"""
Task Coordinator service for CFTeam ecosystem
Manages task creation, assignment, and coordination between agents
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload

from src.config import get_db_session, get_logger, RedisCache, RedisPubSub, CHANNELS
from src.models import Task, TaskStatus, TaskPriority, Session, Agent, Project, AgentStatus


class TaskCoordinator:
    """Coordinates task execution across agents and crews"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = RedisCache()
        self.pubsub = RedisPubSub()
        self._task_queue = []  # In-memory queue for quick access
        
    async def create_task(
        self,
        session_id: int,
        title: str,
        description: str,
        project_id: Optional[int] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        estimated_duration: Optional[int] = None,
        assigned_agent_id: Optional[int] = None
    ) -> Task:
        """Create a new task within a session"""
        try:
            async with get_db_session() as session:
                # Generate unique identifier
                identifier = f"task_{uuid.uuid4().hex[:8]}"
                
                # Create task
                new_task = Task(
                    identifier=identifier,
                    title=title,
                    description=description,
                    session_id=session_id,
                    project_id=project_id,
                    priority=priority,
                    dependencies=dependencies or [],
                    estimated_duration=estimated_duration,
                    assigned_agent_id=assigned_agent_id
                )
                
                session.add(new_task)
                await session.commit()
                await session.refresh(new_task)
                
                # Cache task
                await self.cache.set(
                    f"task:{identifier}",
                    {
                        'id': new_task.id,
                        'title': new_task.title,
                        'status': new_task.status.value,
                        'priority': new_task.priority.value,
                        'assigned_agent_id': new_task.assigned_agent_id
                    },
                    ttl=3600  # 1 hour cache
                )
                
                # Add to queue if not assigned
                if not assigned_agent_id:
                    self._task_queue.append(new_task.id)
                
                # Publish task creation event
                await self.pubsub.publish(
                    CHANNELS['task_updates'],
                    {
                        'action': 'created',
                        'task_id': identifier,
                        'title': title,
                        'session_id': session_id
                    }
                )
                
                self.logger.info(f"Created task: {identifier} - {title}")
                return new_task
                
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            raise
    
    async def get_task(self, identifier: str) -> Optional[Task]:
        """Get task by identifier"""
        try:
            # Check cache first
            cached = await self.cache.get(f"task:{identifier}")
            if cached:
                self.logger.debug(f"Task {identifier} found in cache")
            
            async with get_db_session() as session:
                result = await session.execute(
                    select(Task)
                    .where(Task.identifier == identifier)
                    .options(
                        selectinload(Task.session),
                        selectinload(Task.assigned_agent),
                        selectinload(Task.project)
                    )
                )
                return result.scalar_one_or_none()
                
        except Exception as e:
            self.logger.error(f"Failed to get task {identifier}: {e}")
            return None
    
    async def list_tasks(
        self,
        session_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_agent_id: Optional[int] = None,
        unassigned_only: bool = False
    ) -> List[Task]:
        """List tasks with optional filters"""
        try:
            async with get_db_session() as session:
                query = select(Task)
                
                if session_id:
                    query = query.where(Task.session_id == session_id)
                
                if status:
                    query = query.where(Task.status == status)
                
                if priority:
                    query = query.where(Task.priority == priority)
                
                if assigned_agent_id:
                    query = query.where(Task.assigned_agent_id == assigned_agent_id)
                
                if unassigned_only:
                    query = query.where(Task.assigned_agent_id.is_(None))
                
                query = query.order_by(Task.priority.desc(), Task.created_at)
                
                result = await session.execute(query)
                return result.scalars().all()
                
        except Exception as e:
            self.logger.error(f"Failed to list tasks: {e}")
            return []
    
    async def assign_task(self, task_identifier: str, agent_identifier: str) -> bool:
        """Assign a task to an agent"""
        try:
            async with get_db_session() as session:
                # Get agent
                agent_result = await session.execute(
                    select(Agent).where(Agent.identifier == agent_identifier)
                )
                agent = agent_result.scalar_one_or_none()
                
                if not agent:
                    self.logger.error(f"Agent {agent_identifier} not found")
                    return False
                
                # Update task
                result = await session.execute(
                    update(Task)
                    .where(Task.identifier == task_identifier)
                    .where(Task.status == TaskStatus.PENDING)
                    .values(
                        assigned_agent_id=agent.id,
                        status=TaskStatus.ASSIGNED,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update agent status
                    await session.execute(
                        update(Agent)
                        .where(Agent.id == agent.id)
                        .values(
                            status=AgentStatus.WORKING,
                            last_active_at=datetime.utcnow()
                        )
                    )
                    await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"task:{task_identifier}")
                    
                    # Remove from queue
                    task = await self.get_task(task_identifier)
                    if task and task.id in self._task_queue:
                        self._task_queue.remove(task.id)
                    
                    # Publish assignment event
                    await self.pubsub.publish(
                        CHANNELS['task_updates'],
                        {
                            'action': 'assigned',
                            'task_id': task_identifier,
                            'agent_id': agent_identifier
                        }
                    )
                    
                    self.logger.info(f"Assigned task {task_identifier} to agent {agent_identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to assign task {task_identifier}: {e}")
            return False
    
    async def start_task(self, identifier: str) -> bool:
        """Start task execution"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    update(Task)
                    .where(Task.identifier == identifier)
                    .where(Task.status.in_([TaskStatus.ASSIGNED, TaskStatus.PENDING]))
                    .values(
                        status=TaskStatus.IN_PROGRESS,
                        started_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"task:{identifier}")
                    
                    # Publish status update
                    await self.pubsub.publish(
                        CHANNELS['task_updates'],
                        {
                            'action': 'started',
                            'task_id': identifier
                        }
                    )
                    
                    self.logger.info(f"Started task: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start task {identifier}: {e}")
            return False
    
    async def complete_task(
        self, 
        identifier: str, 
        output: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark task as completed"""
        try:
            async with get_db_session() as session:
                # Get task to calculate duration
                task = await self.get_task(identifier)
                if not task:
                    return False
                
                actual_duration = None
                if task.started_at:
                    actual_duration = int(
                        (datetime.utcnow() - task.started_at).total_seconds() / 60
                    )
                
                result = await session.execute(
                    update(Task)
                    .where(Task.identifier == identifier)
                    .where(Task.status == TaskStatus.IN_PROGRESS)
                    .values(
                        status=TaskStatus.COMPLETED,
                        completed_at=datetime.utcnow(),
                        actual_duration=actual_duration,
                        output=output or {}
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update agent metrics
                    if task.assigned_agent_id:
                        agent_result = await session.execute(
                            select(Agent).where(Agent.id == task.assigned_agent_id)
                        )
                        agent = agent_result.scalar_one()
                        
                        agent.tasks_completed += 1
                        agent.status = AgentStatus.IDLE
                        
                        # Update success rate
                        total_tasks = agent.tasks_completed + agent.tasks_failed
                        agent.success_rate = (agent.tasks_completed / total_tasks) * 100
                        
                        # Update average duration
                        if actual_duration and agent.average_task_duration:
                            agent.average_task_duration = (
                                (agent.average_task_duration * (agent.tasks_completed - 1) + actual_duration) 
                                / agent.tasks_completed
                            )
                        elif actual_duration:
                            agent.average_task_duration = actual_duration
                        
                        await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"task:{identifier}")
                    
                    # Check for dependent tasks
                    await self._check_and_unblock_dependencies(identifier)
                    
                    # Publish completion event
                    await self.pubsub.publish(
                        CHANNELS['task_updates'],
                        {
                            'action': 'completed',
                            'task_id': identifier,
                            'duration_minutes': actual_duration
                        }
                    )
                    
                    self.logger.info(f"Completed task: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to complete task {identifier}: {e}")
            return False
    
    async def fail_task(self, identifier: str, error_message: str) -> bool:
        """Mark task as failed"""
        try:
            async with get_db_session() as session:
                # Get task
                task = await self.get_task(identifier)
                if not task:
                    return False
                
                result = await session.execute(
                    update(Task)
                    .where(Task.identifier == identifier)
                    .where(Task.status != TaskStatus.COMPLETED)
                    .values(
                        status=TaskStatus.FAILED,
                        error_message=error_message,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update agent metrics
                    if task.assigned_agent_id:
                        agent_result = await session.execute(
                            select(Agent).where(Agent.id == task.assigned_agent_id)
                        )
                        agent = agent_result.scalar_one()
                        
                        agent.tasks_failed += 1
                        agent.status = AgentStatus.IDLE
                        agent.last_error = error_message
                        
                        # Update success rate
                        total_tasks = agent.tasks_completed + agent.tasks_failed
                        agent.success_rate = (agent.tasks_completed / total_tasks) * 100
                        
                        await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"task:{identifier}")
                    
                    # Publish failure event
                    await self.pubsub.publish(
                        CHANNELS['task_updates'],
                        {
                            'action': 'failed',
                            'task_id': identifier,
                            'error': error_message
                        }
                    )
                    
                    self.logger.error(f"Failed task: {identifier} - {error_message}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to mark task {identifier} as failed: {e}")
            return False
    
    async def retry_task(self, identifier: str) -> bool:
        """Retry a failed task"""
        try:
            async with get_db_session() as session:
                task = await self.get_task(identifier)
                if not task or task.status != TaskStatus.FAILED:
                    return False
                
                result = await session.execute(
                    update(Task)
                    .where(Task.identifier == identifier)
                    .values(
                        status=TaskStatus.PENDING,
                        retry_count=task.retry_count + 1,
                        error_message=None,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Add back to queue if not assigned
                    if not task.assigned_agent_id:
                        self._task_queue.append(task.id)
                    
                    # Clear cache
                    await self.cache.delete(f"task:{identifier}")
                    
                    # Publish retry event
                    await self.pubsub.publish(
                        CHANNELS['task_updates'],
                        {
                            'action': 'retried',
                            'task_id': identifier,
                            'retry_count': task.retry_count + 1
                        }
                    )
                    
                    self.logger.info(f"Retrying task: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to retry task {identifier}: {e}")
            return False
    
    async def get_next_task_for_agent(self, agent_identifier: str) -> Optional[Task]:
        """Get the next suitable task for an agent"""
        try:
            async with get_db_session() as session:
                # Get agent capabilities
                agent_result = await session.execute(
                    select(Agent).where(Agent.identifier == agent_identifier)
                )
                agent = agent_result.scalar_one_or_none()
                
                if not agent:
                    return None
                
                # Find unassigned tasks matching agent capabilities
                query = select(Task).where(
                    and_(
                        Task.assigned_agent_id.is_(None),
                        Task.status == TaskStatus.PENDING,
                        Task.dependencies == []  # No blocked tasks
                    )
                ).order_by(Task.priority.desc(), Task.created_at)
                
                result = await session.execute(query)
                tasks = result.scalars().all()
                
                # Filter by agent capabilities
                for task in tasks:
                    # TODO: Implement capability matching logic
                    # For now, return first available task
                    return task
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get next task for agent {agent_identifier}: {e}")
            return None
    
    async def _check_and_unblock_dependencies(self, completed_task_identifier: str):
        """Check and unblock tasks dependent on the completed task"""
        try:
            async with get_db_session() as session:
                # Find all blocked tasks
                result = await session.execute(
                    select(Task).where(Task.status == TaskStatus.BLOCKED)
                )
                blocked_tasks = result.scalars().all()
                
                for task in blocked_tasks:
                    if completed_task_identifier in task.dependencies:
                        # Remove completed dependency
                        task.dependencies.remove(completed_task_identifier)
                        
                        # If no more dependencies, unblock task
                        if not task.dependencies:
                            task.status = TaskStatus.PENDING
                            
                            # Add to queue if not assigned
                            if not task.assigned_agent_id:
                                self._task_queue.append(task.id)
                            
                            self.logger.info(f"Unblocked task: {task.identifier}")
                        
                        await session.commit()
                        
        except Exception as e:
            self.logger.error(f"Failed to check dependencies: {e}")
    
    async def get_task_statistics(self, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Get task statistics"""
        try:
            async with get_db_session() as session:
                query = select(Task)
                if session_id:
                    query = query.where(Task.session_id == session_id)
                
                result = await session.execute(query)
                tasks = result.scalars().all()
                
                stats = {
                    'total': len(tasks),
                    'by_status': {},
                    'by_priority': {},
                    'average_duration': 0,
                    'success_rate': 0
                }
                
                # Count by status
                for status in TaskStatus:
                    count = len([t for t in tasks if t.status == status])
                    if count > 0:
                        stats['by_status'][status.value] = count
                
                # Count by priority
                for priority in TaskPriority:
                    count = len([t for t in tasks if t.priority == priority])
                    if count > 0:
                        stats['by_priority'][priority.value] = count
                
                # Calculate average duration
                completed_tasks = [t for t in tasks if t.actual_duration]
                if completed_tasks:
                    stats['average_duration'] = sum(
                        t.actual_duration for t in completed_tasks
                    ) / len(completed_tasks)
                
                # Calculate success rate
                finished_tasks = len([t for t in tasks if t.status in [
                    TaskStatus.COMPLETED, TaskStatus.FAILED
                ]])
                if finished_tasks > 0:
                    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
                    stats['success_rate'] = (completed / finished_tasks) * 100
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get task statistics: {e}")
            return {}