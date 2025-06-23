#!/usr/bin/env python3
"""
Run database migrations for CFTeam ecosystem
Creates all tables based on SQLAlchemy models
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import init_database, create_tables, close_database
from src.config import get_logger


async def run_migrations():
    """Run database migrations"""
    logger = get_logger(__name__)
    
    try:
        logger.info("Starting database migrations...")
        
        # Initialize database connection
        logger.info("Connecting to database...")
        await init_database()
        
        # Create all tables
        logger.info("Creating tables...")
        await create_tables()
        
        logger.info("✅ Database migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # Close database connection
        await close_database()


if __name__ == "__main__":
    print("🚀 CFTeam Database Migration Tool")
    print("-" * 40)
    asyncio.run(run_migrations())