#!/usr/bin/env python3
"""
Quick test script for CFTeam ecosystem
Tests basic functionality without full CrewAI setup
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.config import init_database, init_redis, setup_logging
from src.services import SessionManager, TaskCoordinator
from src.models import SessionPriority, TaskPriority

# Load environment
load_dotenv()


async def test_basic_functionality():
    """Test basic system functionality"""
    print("🚀 Testing CFTeam Basic Functionality")
    print("-" * 50)
    
    try:
        # Setup logging
        setup_logging()
        print("✅ Logging initialized")
        
        # Initialize database
        print("🔄 Initializing database...")
        await init_database()
        print("✅ Database connected")
        
        # Initialize Redis
        print("🔄 Initializing Redis...")
        await init_redis()
        print("✅ Redis connected")
        
        # Test SessionManager
        print("\n📋 Testing SessionManager...")
        session_manager = SessionManager()
        
        # Create a test session
        session = await session_manager.create_session(
            name="Test Development Session",
            description="Testing the CFTeam ecosystem",
            priority=SessionPriority.HIGH,
            projects=["burrow_hub", "ecommerce"]
        )
        print(f"✅ Created session: {session.identifier}")
        
        # Start session
        success = await session_manager.start_session(session.identifier)
        print(f"✅ Started session: {success}")
        
        # Get session progress
        progress = await session_manager.get_session_progress(session.identifier)
        print(f"📊 Session progress: {progress}")
        
        # Test TaskCoordinator
        print("\n📋 Testing TaskCoordinator...")
        task_coordinator = TaskCoordinator()
        
        # Create tasks
        task1 = await task_coordinator.create_task(
            session_id=session.id,
            title="Create PaymentGateway module",
            description="Create a new Laravel module for payment processing",
            priority=TaskPriority.HIGH
        )
        print(f"✅ Created task: {task1.identifier}")
        
        task2 = await task_coordinator.create_task(
            session_id=session.id,
            title="Create payment API endpoints",
            description="Create REST API endpoints for payment operations",
            priority=TaskPriority.HIGH,
            dependencies=[task1.identifier]
        )
        print(f"✅ Created dependent task: {task2.identifier}")
        
        # Get task statistics
        stats = await task_coordinator.get_task_statistics(session.id)
        print(f"📊 Task statistics: {stats}")
        
        # Complete session
        await session_manager.complete_session(
            session.identifier,
            summary="Test completed successfully"
        )
        print(f"✅ Completed session")
        
        print("\n✨ All basic tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_yaml_loading():
    """Test YAML configuration loading"""
    print("\n📄 Testing YAML Configuration Loading...")
    print("-" * 50)
    
    try:
        from src.config import list_available_agents, list_available_crews, list_available_projects
        
        agents = list_available_agents()
        print(f"✅ Loaded {len(agents)} agents: {', '.join(agents[:5])}...")
        
        crews = list_available_crews()
        print(f"✅ Loaded {len(crews)} crews: {', '.join(crews)}")
        
        projects = list_available_projects()
        print(f"✅ Loaded {len(projects)} projects: {', '.join(projects)}")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML loading failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🤖 CFTeam Ecosystem Test Suite")
    print("=" * 50)
    
    # Check environment
    print(f"📍 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"🗄️  Database: {os.getenv('POSTGRES_DB', 'Not configured')}")
    print()
    
    # Run tests
    yaml_ok = await test_yaml_loading()
    basic_ok = await test_basic_functionality()
    
    if yaml_ok and basic_ok:
        print("\n✅ All tests passed! System is ready.")
        print("\n🎯 Next steps:")
        print("   1. Run 'python src/main.py' to start the CLI")
        print("   2. Use 'cfteam' commands as documented")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())