"""
Task model for CFTeam ecosystem
Represents individual tasks within a session
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from src.config.database import Base


class TaskStatus(enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"


class TaskType(enum.Enum):
    """Task type enumeration"""
    DEVELOPMENT = "development"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    REVIEW = "review"


class TaskPriority(enum.Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    task_type = Column(Enum(TaskType), default=TaskType.DEVELOPMENT, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Assignment
    assigned_agent = Column(String(100))  # Agent ID
    assigned_crew = Column(String(100))   # Crew name
    
    # Project information
    project = Column(String(100), nullable=False)  # Project identifier
    module = Column(String(100))  # Module within project
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    due_date = Column(DateTime)
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    
    # Task details
    requirements = Column(JSON, default=list)  # List of requirements
    acceptance_criteria = Column(JSON, default=list)  # List of criteria
    dependencies = Column(JSON, default=list)  # Task IDs this depends on
    
    # Results
    result = Column(JSON, default=dict)  # Task results/output
    artifacts = Column(JSON, default=dict)  # Files created, commits, etc.
    error_details = Column(Text)  # Error information if failed
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Flexible metadata
    tags = Column(JSON, default=list)  # Tags for categorization
    
    # Flags
    is_blocking = Column(Boolean, default=False)  # Blocks other tasks
    requires_review = Column(Boolean, default=False)
    auto_assign = Column(Boolean, default=True)
    
    # Relationships
    # session = relationship("Session", back_populates="tasks")
    # subtasks = relationship("Task", backref="parent_task", remote_side=[id])
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id) if self.session_id else None,
            "parent_task_id": str(self.parent_task_id) if self.parent_task_id else None,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_agent": self.assigned_agent,
            "assigned_crew": self.assigned_crew,
            "project": self.project,
            "module": self.module,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "requirements": self.requirements,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "result": self.result,
            "artifacts": self.artifacts,
            "error_details": self.error_details,
            "metadata": self.metadata,
            "tags": self.tags,
            "is_blocking": self.is_blocking,
            "requires_review": self.requires_review,
            "auto_assign": self.auto_assign,
        }
    
    def start(self):
        """Start the task"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
    
    def complete(self, result: Optional[Dict[str, Any]] = None):
        """Complete the task"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if result:
            self.result = result
        
        # Calculate actual hours if started_at exists
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.actual_hours = int(duration.total_seconds() / 3600)
    
    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_details = error
    
    def block(self, reason: str):
        """Mark task as blocked"""
        self.status = TaskStatus.BLOCKED
        if not self.metadata:
            self.metadata = {}
        self.metadata["block_reason"] = reason
    
    def unblock(self):
        """Unblock the task"""
        if self.status == TaskStatus.BLOCKED:
            self.status = TaskStatus.PENDING
            if self.metadata and "block_reason" in self.metadata:
                del self.metadata["block_reason"]
    
    def cancel(self, reason: Optional[str] = None):
        """Cancel the task"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        if reason:
            if not self.metadata:
                self.metadata = {}
            self.metadata["cancellation_reason"] = reason
    
    def submit_for_review(self):
        """Submit task for review"""
        self.status = TaskStatus.UNDER_REVIEW
        self.requires_review = True
    
    def add_artifact(self, key: str, value: Any):
        """Add an artifact to the task"""
        if not self.artifacts:
            self.artifacts = {}
        self.artifacts[key] = value
    
    def add_dependency(self, task_id: str):
        """Add a dependency to this task"""
        if not self.dependencies:
            self.dependencies = []
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
    
    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """Check if task is ready to start based on dependencies"""
        if not self.dependencies:
            return True
        return all(dep in completed_task_ids for dep in self.dependencies)
    
    def assign_to(self, agent_id: str, crew_name: str):
        """Assign task to an agent and crew"""
        self.assigned_agent = agent_id
        self.assigned_crew = crew_name