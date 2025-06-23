"""
Session Manager service for CFTeam ecosystem
Manages development sessions, tracks progress, and coordinates agents
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from src.config import get_db_session, get_logger, RedisCache, RedisPubSub, CHANNELS
from src.models import Session, SessionStatus, SessionPriority, Task, TaskStatus


class SessionManager:
    """Manages development sessions across the ecosystem"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = RedisCache()
        self.pubsub = RedisPubSub()
        
    async def create_session(
        self,
        name: str,
        description: str,
        priority: SessionPriority = SessionPriority.MEDIUM,
        projects: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new development session"""
        try:
            async with get_db_session() as session:
                # Generate unique identifier
                identifier = f"session_{uuid.uuid4().hex[:8]}"
                
                # Create session
                new_session = Session(
                    identifier=identifier,
                    name=name,
                    description=description,
                    priority=priority,
                    meta_data=metadata or {}
                )
                
                if projects:
                    new_session.meta_data['projects'] = projects
                
                session.add(new_session)
                await session.commit()
                await session.refresh(new_session)
                
                # Cache session
                await self.cache.set(
                    f"session:{identifier}",
                    {
                        'id': new_session.id,
                        'name': new_session.name,
                        'status': new_session.status.value,
                        'priority': new_session.priority.value
                    },
                    ttl=3600  # 1 hour cache
                )
                
                # Publish session creation event
                await self.pubsub.publish(
                    CHANNELS['session_updates'],
                    {
                        'action': 'created',
                        'session_id': identifier,
                        'name': name
                    }
                )
                
                self.logger.info(f"Created session: {identifier} - {name}")
                return new_session
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, identifier: str) -> Optional[Session]:
        """Get session by identifier"""
        try:
            # Check cache first
            cached = await self.cache.get(f"session:{identifier}")
            if cached:
                self.logger.debug(f"Session {identifier} found in cache")
            
            async with get_db_session() as session:
                result = await session.execute(
                    select(Session)
                    .where(Session.identifier == identifier)
                    .options(selectinload(Session.tasks))
                )
                return result.scalar_one_or_none()
                
        except Exception as e:
            self.logger.error(f"Failed to get session {identifier}: {e}")
            return None
    
    async def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        priority: Optional[SessionPriority] = None,
        active_only: bool = False
    ) -> List[Session]:
        """List sessions with optional filters"""
        try:
            async with get_db_session() as session:
                query = select(Session)
                
                if status:
                    query = query.where(Session.status == status)
                
                if priority:
                    query = query.where(Session.priority == priority)
                
                if active_only:
                    query = query.where(
                        Session.status.in_([
                            SessionStatus.PLANNING,
                            SessionStatus.ACTIVE,
                            SessionStatus.PAUSED
                        ])
                    )
                
                query = query.order_by(Session.created_at.desc())
                
                result = await session.execute(query)
                return result.scalars().all()
                
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def start_session(self, identifier: str) -> bool:
        """Start a session (change status to ACTIVE)"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    update(Session)
                    .where(Session.identifier == identifier)
                    .where(Session.status == SessionStatus.PLANNING)
                    .values(
                        status=SessionStatus.ACTIVE,
                        started_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"session:{identifier}")
                    
                    # Publish status update
                    await self.pubsub.publish(
                        CHANNELS['session_updates'],
                        {
                            'action': 'started',
                            'session_id': identifier
                        }
                    )
                    
                    self.logger.info(f"Started session: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start session {identifier}: {e}")
            return False
    
    async def pause_session(self, identifier: str, reason: Optional[str] = None) -> bool:
        """Pause an active session"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    update(Session)
                    .where(Session.identifier == identifier)
                    .where(Session.status == SessionStatus.ACTIVE)
                    .values(
                        status=SessionStatus.PAUSED,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update metadata with pause reason
                    if reason:
                        sess = await self.get_session(identifier)
                        if sess:
                            sess.meta_data['pause_reason'] = reason
                            sess.meta_data['paused_at'] = datetime.utcnow().isoformat()
                            await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"session:{identifier}")
                    
                    # Publish status update
                    await self.pubsub.publish(
                        CHANNELS['session_updates'],
                        {
                            'action': 'paused',
                            'session_id': identifier,
                            'reason': reason
                        }
                    )
                    
                    self.logger.info(f"Paused session: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to pause session {identifier}: {e}")
            return False
    
    async def complete_session(self, identifier: str, summary: Optional[str] = None) -> bool:
        """Complete a session"""
        try:
            async with get_db_session() as session:
                # Check if all tasks are completed
                sess = await self.get_session(identifier)
                if not sess:
                    return False
                
                incomplete_tasks = [
                    task for task in sess.tasks 
                    if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
                ]
                
                if incomplete_tasks:
                    self.logger.warning(
                        f"Session {identifier} has {len(incomplete_tasks)} incomplete tasks"
                    )
                
                result = await session.execute(
                    update(Session)
                    .where(Session.identifier == identifier)
                    .where(Session.status.in_([SessionStatus.ACTIVE, SessionStatus.PAUSED]))
                    .values(
                        status=SessionStatus.COMPLETED,
                        completed_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update metadata with summary
                    if summary:
                        sess.meta_data['completion_summary'] = summary
                        await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"session:{identifier}")
                    
                    # Publish status update
                    await self.pubsub.publish(
                        CHANNELS['session_updates'],
                        {
                            'action': 'completed',
                            'session_id': identifier,
                            'summary': summary
                        }
                    )
                    
                    self.logger.info(f"Completed session: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to complete session {identifier}: {e}")
            return False
    
    async def fail_session(self, identifier: str, error: str) -> bool:
        """Mark session as failed"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    update(Session)
                    .where(Session.identifier == identifier)
                    .where(Session.status != SessionStatus.COMPLETED)
                    .values(
                        status=SessionStatus.FAILED,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Update metadata with error
                    sess = await self.get_session(identifier)
                    if sess:
                        sess.meta_data['failure_reason'] = error
                        sess.meta_data['failed_at'] = datetime.utcnow().isoformat()
                        await session.commit()
                    
                    # Clear cache
                    await self.cache.delete(f"session:{identifier}")
                    
                    # Publish status update
                    await self.pubsub.publish(
                        CHANNELS['session_updates'],
                        {
                            'action': 'failed',
                            'session_id': identifier,
                            'error': error
                        }
                    )
                    
                    self.logger.error(f"Failed session: {identifier} - {error}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to mark session {identifier} as failed: {e}")
            return False
    
    async def get_session_progress(self, identifier: str) -> Dict[str, Any]:
        """Get session progress statistics"""
        try:
            sess = await self.get_session(identifier)
            if not sess:
                return {}
            
            total_tasks = len(sess.tasks)
            completed_tasks = len([t for t in sess.tasks if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in sess.tasks if t.status == TaskStatus.FAILED])
            in_progress_tasks = len([t for t in sess.tasks if t.status == TaskStatus.IN_PROGRESS])
            
            progress = {
                'session_id': sess.identifier,
                'status': sess.status.value,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                'started_at': sess.started_at.isoformat() if sess.started_at else None,
                'duration_minutes': (
                    (datetime.utcnow() - sess.started_at).total_seconds() / 60
                ) if sess.started_at else 0
            }
            
            # Cache progress
            await self.cache.set(
                f"session_progress:{identifier}",
                progress,
                ttl=60  # 1 minute cache
            )
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Failed to get session progress for {identifier}: {e}")
            return {}
    
    async def archive_session(self, identifier: str) -> bool:
        """Archive a completed or failed session"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    update(Session)
                    .where(Session.identifier == identifier)
                    .where(Session.status.in_([SessionStatus.COMPLETED, SessionStatus.FAILED]))
                    .values(
                        status=SessionStatus.ARCHIVED,
                        updated_at=datetime.utcnow()
                    )
                )
                
                if result.rowcount > 0:
                    await session.commit()
                    
                    # Clear all related cache
                    await self.cache.delete(f"session:{identifier}")
                    await self.cache.delete(f"session_progress:{identifier}")
                    
                    self.logger.info(f"Archived session: {identifier}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to archive session {identifier}: {e}")
            return False
    
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Session)
                    .where(Session.status == SessionStatus.ACTIVE)
                )
                return len(result.scalars().all())
                
        except Exception as e:
            self.logger.error(f"Failed to get active sessions count: {e}")
            return 0