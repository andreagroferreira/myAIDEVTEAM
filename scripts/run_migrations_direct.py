#!/usr/bin/env python3
"""
Direct migration runner to avoid circular imports
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Load environment variables
load_dotenv()


class Base(DeclarativeBase):
    """SQLAlchemy base class"""
    pass


async def run_migrations():
    """Run database migrations directly"""
    # Build database URL
    db_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": os.getenv("POSTGRES_DB", "crewai_ecosystem"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "")
    }
    
    DATABASE_URL = f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    print(f"🗄️  Connecting to database: {db_config['database']} at {db_config['host']}:{db_config['port']}")
    
    try:
        # Create engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # Show SQL statements
            pool_size=5,
            max_overflow=10,
        )
        
        # Import models after Base is defined
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Import models directly to register them
        from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, Enum, ForeignKey
        from sqlalchemy.orm import relationship
        from datetime import datetime
        import enum
        
        # Define enums
        class SessionStatus(str, enum.Enum):
            PLANNING = "planning"
            ACTIVE = "active"
            PAUSED = "paused"
            COMPLETED = "completed"
            FAILED = "failed"
            ARCHIVED = "archived"
        
        class SessionPriority(str, enum.Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            URGENT = "urgent"
            CRITICAL = "critical"
        
        class TaskStatus(str, enum.Enum):
            PENDING = "pending"
            ASSIGNED = "assigned"
            IN_PROGRESS = "in_progress"
            REVIEWING = "reviewing"
            COMPLETED = "completed"
            FAILED = "failed"
            CANCELLED = "cancelled"
            BLOCKED = "blocked"
        
        class TaskPriority(str, enum.Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"
            URGENT = "urgent"
        
        class ProjectType(str, enum.Enum):
            LARAVEL = "laravel"
            NUXT = "nuxt"
            VUE = "vue"
            REACT = "react"
            DJANGO = "django"
            FLASK = "flask"
            FASTAPI = "fastapi"
            MICROSERVICE = "microservice"
            API = "api"
            LIBRARY = "library"
            OTHER = "other"
        
        class ProjectStatus(str, enum.Enum):
            ACTIVE = "active"
            DEVELOPMENT = "development"
            MAINTENANCE = "maintenance"
            PAUSED = "paused"
            ARCHIVED = "archived"
        
        class AgentTier(str, enum.Enum):
            MANAGEMENT = "management"
            DEVELOPMENT = "development"
            QUALITY = "quality"
            INTELLIGENCE = "intelligence"
            INTEGRATION = "integration"
        
        class AgentStatus(str, enum.Enum):
            IDLE = "idle"
            WORKING = "working"
            PAUSED = "paused"
            ERROR = "error"
            MAINTENANCE = "maintenance"
        
        # Define models
        class Session(Base):
            __tablename__ = "sessions"
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            identifier = Column(String(100), unique=True, nullable=False, index=True)
            name = Column(String(255), nullable=False)
            description = Column(Text)
            status = Column(Enum(SessionStatus), default=SessionStatus.PLANNING, nullable=False)
            priority = Column(Enum(SessionPriority), default=SessionPriority.MEDIUM, nullable=False)
            meta_data = Column(JSON, default={})
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            started_at = Column(DateTime)
            completed_at = Column(DateTime)
            
            # Relationships
            tasks = relationship("Task", back_populates="session", cascade="all, delete-orphan")
        
        class Task(Base):
            __tablename__ = "tasks"
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            identifier = Column(String(100), unique=True, nullable=False, index=True)
            title = Column(String(255), nullable=False)
            description = Column(Text)
            status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
            priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
            
            # Relationships
            session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
            session = relationship("Session", back_populates="tasks")
            
            assigned_agent_id = Column(Integer, ForeignKey("agents.id"))
            assigned_agent = relationship("Agent", back_populates="tasks")
            
            project_id = Column(Integer, ForeignKey("projects.id"))
            project = relationship("Project", back_populates="tasks")
            
            # Task details
            dependencies = Column(JSON, default=[])
            output = Column(JSON)
            error_message = Column(Text)
            
            # Metrics
            estimated_duration = Column(Integer)  # minutes
            actual_duration = Column(Integer)  # minutes
            retry_count = Column(Integer, default=0)
            
            # Timestamps
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            started_at = Column(DateTime)
            completed_at = Column(DateTime)
        
        class Project(Base):
            __tablename__ = "projects"
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            identifier = Column(String(100), unique=True, nullable=False, index=True)
            name = Column(String(255), nullable=False)
            description = Column(Text)
            project_type = Column(Enum(ProjectType), nullable=False)
            status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
            
            # Project details
            path = Column(String(500), nullable=False)
            repository_url = Column(String(500))
            database_type = Column(String(50))
            primary_language = Column(String(50))
            framework_version = Column(String(50))
            
            # Configuration
            dependencies = Column(JSON, default={})
            build_commands = Column(JSON, default={})
            quality_thresholds = Column(JSON, default={})
            integrations = Column(JSON, default=[])
            
            # Metadata
            meta_data = Column(JSON, default={})
            
            # Timestamps
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            last_synced_at = Column(DateTime)
            
            # Relationships
            tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
        
        class Agent(Base):
            __tablename__ = "agents"
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            identifier = Column(String(100), unique=True, nullable=False, index=True)
            name = Column(String(255), nullable=False)
            role = Column(String(100), nullable=False)
            tier = Column(Enum(AgentTier), nullable=False)
            status = Column(Enum(AgentStatus), default=AgentStatus.IDLE, nullable=False)
            
            # Agent capabilities
            capabilities = Column(JSON, default=[])
            tools = Column(JSON, default=[])
            max_rpm = Column(Integer, default=20)
            allow_delegation = Column(Boolean, default=False)
            
            # Performance metrics
            tasks_completed = Column(Integer, default=0)
            tasks_failed = Column(Integer, default=0)
            average_task_duration = Column(Float)
            success_rate = Column(Float)
            last_error = Column(Text)
            
            # Configuration
            config = Column(JSON, default={})
            
            # Timestamps
            created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
            last_active_at = Column(DateTime)
            
            # Relationships
            tasks = relationship("Task", back_populates="assigned_agent")
        
        # Create all tables
        print("\n📊 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("\n✅ Database migrations completed successfully!")
        
        # Show created tables
        print("\n📋 Created tables:")
        for table in Base.metadata.tables:
            print(f"   - {table}")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\n🔧 Please ensure:")
        print("   1. PostgreSQL is running in DBngin")
        print("   2. Database 'crewai_ecosystem' exists")
        print("   3. .env file has correct credentials")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 CFTeam Direct Database Migration Tool")
    print("-" * 40)
    
    # Check if .env exists
    from pathlib import Path
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env and configure your database settings")
        exit(1)
    
    success = asyncio.run(run_migrations())
    exit(0 if success else 1)