#!/bin/bash
set -e

echo "🚀 Setting up CFTeam CrewAI Environment..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version detected"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check DBngin services
echo "🗄️ Checking DBngin services..."
echo "📋 Please ensure in DBngin:"
echo "   - PostgreSQL server is running (port 5432)"
echo "   - Redis server is running (port 6379)"
echo "   - Database 'crewai_ecosystem' exists"

# Test database connection
echo "🔍 Testing database connection..."
python -c "
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    print('✅ PostgreSQL connection successful')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    print('🔧 Please check your DBngin PostgreSQL settings')
"

# Test Redis connection
echo "🔍 Testing Redis connection..."
python -c "
import redis
import os
from dotenv import load_dotenv

load_dotenv()

try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        db=int(os.getenv('REDIS_DB'))
    )
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    print('🔧 Please check your DBngin Redis settings or install via Homebrew')
"

# Run database migrations
echo "🗃️ Setting up database schema..."
python -c "
import asyncio
from src.config.database import init_database, create_tables

async def setup():
    await init_database()
    await create_tables()

asyncio.run(setup())
"

# Setup CLI alias
echo "🔧 Setting up CLI alias..."
echo "alias cfteam='cd /Users/andreagroferreira/Work/CFTeam && source venv/bin/activate && python src/main.py'" >> ~/.zshrc

echo "✅ CFTeam environment setup complete!"
echo "💡 Run 'source ~/.zshrc' then 'cfteam' to start"
echo ""
echo "📋 DBngin Requirements:"
echo "   ✓ PostgreSQL server running on port 5432"
echo "   ✓ Redis server running on port 6379"
echo "   ✓ Database 'crewai_ecosystem' created"
echo "   ✓ Update .env file with your DBngin credentials"