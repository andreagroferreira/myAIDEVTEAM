"""
Session model for CFTeam ecosystem
Manages development sessions across multiple projects
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from src.config.database import Base


class SessionStatus(enum.Enum):
    """Session status enumeration"""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionPriority(enum.Enum):
    """Session priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Session(Base):
    """Development session model"""
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(SessionStatus), default=SessionStatus.CREATED, nullable=False)
    priority = Column(Enum(SessionPriority), default=SessionPriority.MEDIUM, nullable=False)
    
    # Projects involved
    projects = Column(JSON, default=list)  # List of project identifiers
    primary_project = Column(String(100))  # Main project for this session
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    estimated_duration = Column(String(50))  # e.g., "2 hours", "1 day"
    
    # User information
    initiated_by = Column(String(100))  # User or system that initiated
    assigned_to = Column(JSON, default=list)  # List of assigned agents/crews
    
    # Session metadata
    meta_data = Column(JSON, default=dict)  # Flexible metadata storage
    tags = Column(JSON, default=list)  # Tags for categorization
    
    # Coordination flags
    requires_coordination = Column(Boolean, default=False)
    is_emergency = Column(Boolean, default=False)
    auto_coordinate = Column(Boolean, default=True)
    
    # Results and artifacts
    result_summary = Column(Text)
    artifacts = Column(JSON, default=dict)  # Files created, commits made, etc.
    
    # Relationships (to be defined when other models are created)
    # tasks = relationship("Task", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, name='{self.name}', status={self.status.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "projects": self.projects,
            "primary_project": self.primary_project,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "estimated_duration": self.estimated_duration,
            "initiated_by": self.initiated_by,
            "assigned_to": self.assigned_to,
            "metadata": self.meta_data,
            "tags": self.tags,
            "requires_coordination": self.requires_coordination,
            "is_emergency": self.is_emergency,
            "auto_coordinate": self.auto_coordinate,
            "result_summary": self.result_summary,
            "artifacts": self.artifacts,
        }
    
    def start(self):
        """Start the session"""
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.last_active_at = datetime.utcnow()
    
    def complete(self, summary: Optional[str] = None):
        """Complete the session"""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.last_active_at = datetime.utcnow()
        if summary:
            self.result_summary = summary
    
    def pause(self):
        """Pause the session"""
        self.status = SessionStatus.PAUSED
        self.last_active_at = datetime.utcnow()
    
    def resume(self):
        """Resume the session"""
        self.status = SessionStatus.ACTIVE
        self.last_active_at = datetime.utcnow()
    
    def cancel(self, reason: Optional[str] = None):
        """Cancel the session"""
        self.status = SessionStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        if reason:
            if not self.meta_data:
                self.meta_data = {}
            self.meta_data["cancellation_reason"] = reason
    
    def add_artifact(self, key: str, value: Any):
        """Add an artifact to the session"""
        if not self.artifacts:
            self.artifacts = {}
        self.artifacts[key] = value
        self.last_active_at = datetime.utcnow()
    
    def add_tag(self, tag: str):
        """Add a tag to the session"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def assign_to_agent(self, agent_id: str):
        """Assign session to an agent"""
        if not self.assigned_to:
            self.assigned_to = []
        if agent_id not in self.assigned_to:
            self.assigned_to.append(agent_id)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_active_at = datetime.utcnow()