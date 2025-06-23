"""
Agent model for CFTeam ecosystem
Represents AI agents in the system
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, Boolean, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.config.database import Base


class AgentRole(enum.Enum):
    """Agent role enumeration"""
    TECHNICAL_DIRECTOR = "technical_director"
    PROJECT_MANAGER = "project_manager"
    QA_MANAGER = "qa_manager"
    LARAVEL_ARCHITECT = "laravel_architect"
    VUE_ARCHITECT = "vue_architect"
    MODULE_BUILDER = "module_builder"
    API_DESIGNER = "api_designer"
    PAYMENT_GATEWAY = "payment_gateway"
    CODE_QUALITY_LEAD = "code_quality_lead"
    PHPSTAN_VALIDATOR = "phpstan_validator"
    PINT_FORMATTER = "pint_formatter"
    TEST_RUNNER = "test_runner"
    CONTEXT_SEVEN = "context_seven"
    NOTION_MANAGER = "notion_manager"
    SUPABASE_INTELLIGENCE = "supabase_intelligence"
    CROSS_PROJECT_SYNC = "cross_project_sync"
    DATA_CONSISTENCY = "data_consistency"
    DEPLOYMENT_MANAGER = "deployment_manager"


class AgentStatus(enum.Enum):
    """Agent status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentTier(enum.Enum):
    """Agent tier/category"""
    MANAGEMENT = "management"
    DEVELOPMENT = "development"
    QUALITY = "quality"
    INTELLIGENCE = "intelligence"
    INTEGRATION = "integration"


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    identifier = Column(String(100), unique=True, nullable=False)  # e.g., "technical_director"
    name = Column(String(255), nullable=False)  # Display name
    role = Column(Enum(AgentRole), nullable=False)
    tier = Column(Enum(AgentTier), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.AVAILABLE, nullable=False)
    
    # Agent configuration
    goal = Column(Text, nullable=False)  # Agent's primary goal
    backstory = Column(Text)  # Agent's backstory/context
    capabilities = Column(JSON, default=list)  # List of capabilities
    tools = Column(JSON, default=list)  # Available tools
    
    # Performance settings
    max_rpm = Column(Integer, default=20)  # Max requests per minute
    max_concurrent_tasks = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=300)  # Task timeout
    retry_attempts = Column(Integer, default=3)
    
    # Delegation settings
    allow_delegation = Column(Boolean, default=False)
    can_manage_crew = Column(Boolean, default=False)
    delegation_rules = Column(JSON, default=dict)
    
    # Current state
    current_task_id = Column(UUID(as_uuid=True))  # Current task being worked on
    current_session_id = Column(UUID(as_uuid=True))  # Current session
    assigned_projects = Column(JSON, default=list)  # Projects agent is assigned to
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    total_execution_time = Column(Float, default=0.0)  # In seconds
    average_task_time = Column(Float, default=0.0)  # In seconds
    success_rate = Column(Float, default=100.0)  # Percentage
    
    # Resource usage
    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    api_calls_made = Column(Integer, default=0)
    tokens_consumed = Column(Integer, default=0)
    
    # Metadata
    meta_data = Column(JSON, default=dict)
    configuration = Column(JSON, default=dict)  # Additional configuration
    last_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime)
    last_error_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, identifier='{self.identifier}', role={self.role.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "id": str(self.id),
            "identifier": self.identifier,
            "name": self.name,
            "role": self.role.value,
            "tier": self.tier.value,
            "status": self.status.value,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "max_rpm": self.max_rpm,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "allow_delegation": self.allow_delegation,
            "can_manage_crew": self.can_manage_crew,
            "delegation_rules": self.delegation_rules,
            "current_task_id": str(self.current_task_id) if self.current_task_id else None,
            "current_session_id": str(self.current_session_id) if self.current_session_id else None,
            "assigned_projects": self.assigned_projects,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_execution_time": self.total_execution_time,
            "average_task_time": self.average_task_time,
            "success_rate": self.success_rate,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "api_calls_made": self.api_calls_made,
            "tokens_consumed": self.tokens_consumed,
            "metadata": self.meta_data,
            "configuration": self.configuration,
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "last_error_at": self.last_error_at.isoformat() if self.last_error_at else None,
        }
    
    def set_busy(self, task_id: Optional[str] = None, session_id: Optional[str] = None):
        """Set agent as busy"""
        self.status = AgentStatus.BUSY
        if task_id:
            self.current_task_id = uuid.UUID(task_id)
        if session_id:
            self.current_session_id = uuid.UUID(session_id)
        self.last_active_at = datetime.utcnow()
    
    def set_available(self):
        """Set agent as available"""
        self.status = AgentStatus.AVAILABLE
        self.current_task_id = None
        self.last_active_at = datetime.utcnow()
    
    def set_offline(self):
        """Set agent as offline"""
        self.status = AgentStatus.OFFLINE
        self.current_task_id = None
        self.current_session_id = None
    
    def set_error(self, error_message: str):
        """Set agent in error state"""
        self.status = AgentStatus.ERROR
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
    
    def record_task_completion(self, execution_time: float, success: bool = True):
        """Record task completion metrics"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        self.total_execution_time += execution_time
        total_tasks = self.tasks_completed + self.tasks_failed
        
        if total_tasks > 0:
            self.average_task_time = self.total_execution_time / total_tasks
            self.success_rate = (self.tasks_completed / total_tasks) * 100
        
        self.last_active_at = datetime.utcnow()
    
    def update_resource_usage(self, memory_mb: float, cpu_percent: float, 
                            api_calls: int = 0, tokens: int = 0):
        """Update resource usage metrics"""
        self.memory_usage_mb = memory_mb
        self.cpu_usage_percent = cpu_percent
        self.api_calls_made += api_calls
        self.tokens_consumed += tokens
        self.last_active_at = datetime.utcnow()
    
    def add_capability(self, capability: str):
        """Add a capability to the agent"""
        if not self.capabilities:
            self.capabilities = []
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_tool(self, tool: str):
        """Add a tool to the agent"""
        if not self.tools:
            self.tools = []
        if tool not in self.tools:
            self.tools.append(tool)
    
    def assign_to_project(self, project_id: str):
        """Assign agent to a project"""
        if not self.assigned_projects:
            self.assigned_projects = []
        if project_id not in self.assigned_projects:
            self.assigned_projects.append(project_id)
    
    def remove_from_project(self, project_id: str):
        """Remove agent from a project"""
        if self.assigned_projects and project_id in self.assigned_projects:
            self.assigned_projects.remove(project_id)
    
    def is_available_for_task(self) -> bool:
        """Check if agent is available for a new task"""
        return self.status == AgentStatus.AVAILABLE
    
    def can_handle_capability(self, required_capability: str) -> bool:
        """Check if agent has a specific capability"""
        return self.capabilities and required_capability in self.capabilities