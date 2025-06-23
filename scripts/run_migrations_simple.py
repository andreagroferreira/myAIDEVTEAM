#!/usr/bin/env python3
"""
Simple migration runner that doesn't depend on CrewAI
Just creates the database tables using SQLAlchemy
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import only what we need for migrations
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from src.models import Base

# Load environment variables
load_dotenv()


async def run_migrations():
    """Run database migrations without full ecosystem initialization"""
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
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 CFTeam Simple Database Migration Tool")
    print("-" * 40)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env and configure your database settings")
        sys.exit(1)
    
    asyncio.run(run_migrations())