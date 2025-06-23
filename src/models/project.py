"""
Project model for CFTeam ecosystem
Represents managed projects in the ecosystem
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.config.database import Base


class ProjectType(enum.Enum):
    """Project type enumeration"""
    LARAVEL = "laravel"
    NUXT = "nuxt"
    VUE = "vue"
    API = "api"
    MICROSERVICE = "microservice"
    LIBRARY = "library"
    OTHER = "other"


class ProjectStatus(enum.Enum):
    """Project status"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"
    ARCHIVED = "archived"
    PAUSED = "paused"


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    identifier = Column(String(100), unique=True, nullable=False)  # e.g., "burrow_hub"
    name = Column(String(255), nullable=False)  # e.g., "Burrow Hub CRM"
    description = Column(Text)
    project_type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    
    # Paths and locations
    path = Column(String(500), nullable=False)  # File system path
    repository_url = Column(String(500))  # Git repository URL
    documentation_url = Column(String(500))  # Documentation URL
    
    # Database configuration
    database_type = Column(String(50))  # postgresql, supabase, api_driven, etc.
    database_config = Column(JSON, default=dict)  # Connection details (encrypted)
    
    # Technology stack
    primary_language = Column(String(50))  # php, javascript, typescript
    framework_version = Column(String(50))  # Laravel 11, Vue 3, etc.
    dependencies = Column(JSON, default=dict)  # Key dependencies and versions
    
    # Team configuration
    primary_crews = Column(JSON, default=list)  # List of crew names
    assigned_agents = Column(JSON, default=list)  # List of agent IDs
    
    # Integration points
    integrations = Column(JSON, default=dict)  # APIs, services this project integrates with
    exposed_apis = Column(JSON, default=dict)  # APIs this project exposes
    
    # Configuration
    environment_variables = Column(JSON, default=dict)  # Required env vars (keys only)
    build_commands = Column(JSON, default=dict)  # Build, test, deploy commands
    quality_thresholds = Column(JSON, default=dict)  # Coverage, complexity thresholds
    
    # Metadata
    meta_data = Column(JSON, default=dict)  # Flexible metadata storage
    tags = Column(JSON, default=list)  # Project tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_deployed_at = Column(DateTime)
    
    # Flags
    auto_deploy = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    is_critical = Column(Boolean, default=False)  # Critical infrastructure
    
    def __repr__(self):
        return f"<Project(id={self.id}, identifier='{self.identifier}', name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary"""
        return {
            "id": str(self.id),
            "identifier": self.identifier,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type.value,
            "status": self.status.value,
            "path": self.path,
            "repository_url": self.repository_url,
            "documentation_url": self.documentation_url,
            "database_type": self.database_type,
            "database_config": self.database_config,
            "primary_language": self.primary_language,
            "framework_version": self.framework_version,
            "dependencies": self.dependencies,
            "primary_crews": self.primary_crews,
            "assigned_agents": self.assigned_agents,
            "integrations": self.integrations,
            "exposed_apis": self.exposed_apis,
            "environment_variables": self.environment_variables,
            "build_commands": self.build_commands,
            "quality_thresholds": self.quality_thresholds,
            "metadata": self.meta_data,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_deployed_at": self.last_deployed_at.isoformat() if self.last_deployed_at else None,
            "auto_deploy": self.auto_deploy,
            "requires_approval": self.requires_approval,
            "is_critical": self.is_critical,
        }
    
    def add_crew(self, crew_name: str):
        """Add a crew to the project"""
        if not self.primary_crews:
            self.primary_crews = []
        if crew_name not in self.primary_crews:
            self.primary_crews.append(crew_name)
    
    def remove_crew(self, crew_name: str):
        """Remove a crew from the project"""
        if self.primary_crews and crew_name in self.primary_crews:
            self.primary_crews.remove(crew_name)
    
    def add_agent(self, agent_id: str):
        """Assign an agent to the project"""
        if not self.assigned_agents:
            self.assigned_agents = []
        if agent_id not in self.assigned_agents:
            self.assigned_agents.append(agent_id)
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the project"""
        if self.assigned_agents and agent_id in self.assigned_agents:
            self.assigned_agents.remove(agent_id)
    
    def set_build_command(self, command_type: str, command: str):
        """Set a build command"""
        if not self.build_commands:
            self.build_commands = {}
        self.build_commands[command_type] = command
    
    def get_build_command(self, command_type: str) -> Optional[str]:
        """Get a build command"""
        if self.build_commands:
            return self.build_commands.get(command_type)
        return None
    
    def set_quality_threshold(self, metric: str, threshold: Any):
        """Set a quality threshold"""
        if not self.quality_thresholds:
            self.quality_thresholds = {}
        self.quality_thresholds[metric] = threshold
    
    def add_integration(self, service: str, config: Dict[str, Any]):
        """Add an integration"""
        if not self.integrations:
            self.integrations = {}
        self.integrations[service] = config
    
    def add_exposed_api(self, endpoint: str, details: Dict[str, Any]):
        """Add an exposed API endpoint"""
        if not self.exposed_apis:
            self.exposed_apis = {}
        self.exposed_apis[endpoint] = details
    
    def is_active(self) -> bool:
        """Check if project is active"""
        return self.status == ProjectStatus.ACTIVE
    
    def mark_deployed(self):
        """Mark project as deployed"""
        self.last_deployed_at = datetime.utcnow()


# Predefined project configurations
DEFAULT_PROJECTS = [
    {
        "identifier": "burrow_hub",
        "name": "Burrow Hub CRM",
        "project_type": ProjectType.LARAVEL,
        "path": "/Users/andreagroferreira/Herd/burrowhub",
        "database_type": "supabase",
        "primary_language": "php",
        "framework_version": "Laravel 11",
        "primary_crews": ["backend_development_crew", "management_crew", "quality_assurance_crew"],
    },
    {
        "identifier": "ecommerce",
        "name": "E-commerce Frontend",
        "project_type": ProjectType.NUXT,
        "path": "/Users/andreagroferreira/Work/ecommerce",
        "database_type": "api_driven",
        "primary_language": "javascript",
        "framework_version": "Nuxt 3",
        "primary_crews": ["frontend_development_crew", "integration_crew"],
    },
    {
        "identifier": "flownetwork",
        "name": "FlowNetwork Integration MS",
        "project_type": ProjectType.MICROSERVICE,
        "path": "/Users/andreagroferreira/Herd/flownetwork-integration-ms",
        "database_type": "postgresql",
        "primary_language": "php",
        "framework_version": "Laravel 11",
        "primary_crews": ["backend_development_crew", "integration_crew"],
    },
    {
        "identifier": "goblinledger",
        "name": "GoblinLedger Primavera MS",
        "project_type": ProjectType.MICROSERVICE,
        "path": "/Users/andreagroferreira/Herd/goblinledger",
        "database_type": "postgresql",
        "primary_language": "php",
        "framework_version": "Laravel 11",
        "primary_crews": ["backend_development_crew", "integration_crew"],
    },
]