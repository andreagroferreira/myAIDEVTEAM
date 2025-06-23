"""
Database configuration for CFTeam ecosystem
Handles PostgreSQL connections using asyncpg and SQLAlchemy
"""

import os
from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration from environment
DATABASE_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'crewai_ecosystem'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
}

# SQLAlchemy configuration
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Naming convention for database constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Global engine and session factory
engine: Optional[AsyncEngine] = None
async_session_factory: Optional[sessionmaker] = None


async def init_database():
    """Initialize database connection and create engine"""
    global engine, async_session_factory
    
    try:
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=os.getenv('DEBUG', 'false').lower() == 'true',
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Create session factory
        async_session_factory = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        logger.info("Database engine initialized successfully")
        
        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: conn.execute("SELECT 1"))
            logger.info("Database connection test successful")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db_session() -> AsyncSession:
    """Get database session for operations"""
    if async_session_factory is None:
        await init_database()
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    if engine is None:
        await init_database()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def drop_tables():
    """Drop all database tables (use with caution!)"""
    if engine is None:
        await init_database()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")


async def close_database():
    """Close database connections"""
    global engine
    if engine:
        await engine.dispose()
        engine = None
        logger.info("Database connections closed")


class DatabasePool:
    """Manage direct asyncpg connection pool for raw SQL operations"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            min_size=10,
            max_size=20,
            command_timeout=60,
        )
        logger.info("AsyncPG connection pool initialized")
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("AsyncPG connection pool closed")
    
    async def execute(self, query: str, *args):
        """Execute a query"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)


# Global database pool instance
db_pool = DatabasePool()


# Health check function
async def health_check() -> dict:
    """Check database health"""
    try:
        # Check SQLAlchemy connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: conn.execute("SELECT 1"))
        
        # Check asyncpg pool
        if db_pool.pool:
            async with db_pool.pool.acquire() as connection:
                await connection.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "engine": "connected",
            "pool": "connected" if db_pool.pool else "not initialized"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }