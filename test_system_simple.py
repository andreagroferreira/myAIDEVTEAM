#!/usr/bin/env python3
"""
Simple test script for CFTeam ecosystem
Tests only database and basic functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment
load_dotenv()


async def test_database_only():
    """Test only database functionality"""
    print("🚀 Testing CFTeam Database Connection")
    print("-" * 50)
    
    try:
        # Import minimal dependencies
        from src.config.database import init_database, create_tables, get_db_session
        from src.config.redis_config import init_redis, get_redis_client
        
        # Initialize database
        print("🔄 Initializing database...")
        await init_database()
        print("✅ Database connected")
        
        # Initialize Redis
        print("🔄 Initializing Redis...")
        await init_redis()
        redis = await get_redis_client()
        await redis.ping()
        print("✅ Redis connected")
        
        # Test database operations
        print("\n📋 Testing Database Operations...")
        from src.models.session import Session, SessionStatus, SessionPriority
        
        async with get_db_session() as db:
            # Create a test session
            test_session = Session(
                identifier="test_session_001",
                name="Test Session",
                description="Testing database operations",
                status=SessionStatus.CREATED,
                priority=SessionPriority.HIGH
            )
            
            db.add(test_session)
            await db.commit()
            await db.refresh(test_session)
            
            print(f"✅ Created session: {test_session.identifier}")
            
            # Query the session
            from sqlalchemy import select
            result = await db.execute(
                select(Session).where(Session.identifier == "test_session_001")
            )
            found_session = result.scalar_one_or_none()
            
            if found_session:
                print(f"✅ Found session: {found_session.name}")
                
                # Clean up
                await db.delete(found_session)
                await db.commit()
                print("✅ Cleaned up test data")
        
        print("\n✨ Database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_yaml_configs():
    """Test YAML configuration loading without circular imports"""
    print("\n📄 Testing YAML Configuration Files...")
    print("-" * 50)
    
    try:
        import yaml
        from pathlib import Path
        
        config_dir = Path("src/config")
        
        # Test agents.yaml
        with open(config_dir / "agents.yaml", 'r') as f:
            agents = yaml.safe_load(f)
            print(f"✅ Loaded {len(agents)} agents from agents.yaml")
        
        # Test crews.yaml
        with open(config_dir / "crews.yaml", 'r') as f:
            crews = yaml.safe_load(f)
            print(f"✅ Loaded {len(crews)} crews from crews.yaml")
        
        # Test projects.yaml
        with open(config_dir / "projects.yaml", 'r') as f:
            projects_data = yaml.safe_load(f)
            projects = projects_data.get('projects', {})
            print(f"✅ Loaded {len(projects)} projects from projects.yaml")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML loading failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🤖 CFTeam Ecosystem Simple Test")
    print("=" * 50)
    
    # Check environment
    print(f"📍 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"🗄️  Database: {os.getenv('POSTGRES_DB', 'Not configured')}")
    print()
    
    # Run tests
    yaml_ok = await test_yaml_configs()
    db_ok = await test_database_only()
    
    if yaml_ok and db_ok:
        print("\n✅ Basic tests passed! Core functionality is working.")
        print("\n⚠️  Note: Full CrewAI functionality requires Python 3.10+")
        print("\n🎯 Next steps:")
        print("   1. Upgrade to Python 3.10+ for full functionality")
        print("   2. Or continue with limited functionality on Python 3.9")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())