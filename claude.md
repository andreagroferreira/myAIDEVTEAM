# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🤖 CrewAI Multi-Project Development Team

**Project Path:** `/Users/andreagroferreira/Work/CFTeam`  
**Purpose:** Advanced AI agent ecosystem for coordinated development across Laravel CRM/E-commerce projects  
**Integration:** Claude Code + CrewAI + PostgreSQL + Redis + MCPs

---

## 🎯 **PROJECT OVERVIEW**

### **Ecosystem Architecture**
```
CFTeam (Agent Orchestration)
├── 🏢 Burrow Hub CRM (/Users/andreagroferreira/Herd/burrowhub)
├── 🛍️ E-commerce Frontend (/Users/andreagroferreira/Work/ecommerce) 
├── 🔄 FlowNetwork MS (/Users/andreagroferreira/Herd/flownetwork-integration-ms)
└── 💼 GoblinLedger MS (/Users/andreagroferreira/Herd/goblinledger)
```

### **Core Technologies**
- **CrewAI Framework** - Agent orchestration and collaboration
- **PostgreSQL** - Persistent ecosystem state and coordination
- **Redis** - Real-time communication and task queues
- **MCPs Integration** - Context7, Notion, Supabase intelligence
- **Claude Code** - Primary development interface

---

## 🏗️ **IMPLEMENTATION STRUCTURE**

### **Project Directory Structure**
```
/Users/andreagroferreira/Work/CFTeam/
├── README.md
├── requirements.txt
├── .env.example
├── .env                            # DBngin connection settings
├── setup.py
├── 
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py             # PostgreSQL connection
│   │   ├── redis_config.py         # Redis connection
│   │   ├── agents.yaml             # Agent definitions
│   │   ├── crews.yaml              # Crew configurations
│   │   └── projects.yaml           # Project paths and configs
│   │
│   ├── agents/                     # Individual agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── management/
│   │   │   ├── technical_director.py
│   │   │   ├── project_manager.py
│   │   │   └── qa_manager.py
│   │   ├── development/
│   │   │   ├── laravel_architect.py
│   │   │   ├── vue_architect.py
│   │   │   ├── module_builder.py
│   │   │   ├── api_designer.py
│   │   │   └── payment_gateway.py
│   │   ├── quality/
│   │   │   ├── code_quality_lead.py
│   │   │   ├── phpstan_validator.py
│   │   │   ├── pint_formatter.py
│   │   │   └── test_runner.py
│   │   ├── intelligence/
│   │   │   ├── context_seven.py
│   │   │   ├── notion_manager.py
│   │   │   └── supabase_intelligence.py
│   │   └── integration/
│   │       ├── cross_project_sync.py
│   │       ├── data_consistency.py
│   │       └── deployment_manager.py
│   │
│   ├── crews/                      # Crew definitions and workflows
│   │   ├── __init__.py
│   │   ├── management_crew.py
│   │   ├── backend_crew.py
│   │   ├── frontend_crew.py
│   │   ├── integration_crew.py
│   │   ├── quality_crew.py
│   │   └── intelligence_crew.py
│   │
│   ├── workflows/                  # CrewAI Flows
│   │   ├── __init__.py
│   │   ├── development_flow.py
│   │   ├── critical_fix_flow.py
│   │   ├── cross_project_sync_flow.py
│   │   └── deployment_flow.py
│   │
│   ├── tools/                      # Custom tools for agents
│   │   ├── __init__.py
│   │   ├── git_tools.py
│   │   ├── laravel_tools.py
│   │   ├── vue_tools.py
│   │   ├── database_tools.py
│   │   └── mcp_integrations.py
│   │
│   ├── models/                     # Data models and schemas
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── task.py
│   │   ├── project.py
│   │   └── agent.py
│   │
│   ├── services/                   # Business logic services
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── task_coordinator.py
│   │   ├── git_coordinator.py
│   │   └── notification_service.py
│   │
│   └── cli/                        # Command line interface
│       ├── __init__.py
│       ├── commands.py
│       ├── dashboard.py
│       └── session_manager.py
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_crews.py
│   ├── test_workflows.py
│   └── test_integration.py
│
├── scripts/
│   ├── setup_environment.sh
│   ├── start_services.sh
│   ├── stop_services.sh
│   └── backup_ecosystem.sh
│
└── docs/
    ├── architecture.md
    ├── agent_specifications.md
    ├── workflow_documentation.md
    └── troubleshooting.md
```

---

## 🚀 **INSTALLATION INSTRUCTIONS**

### **Step 1: Environment Setup**

```bash
# Create project directory
mkdir -p /Users/andreagroferreira/Work/CFTeam
cd /Users/andreagroferreira/Work/CFTeam

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install crewai[tools] asyncpg redis python-dotenv pydantic sqlalchemy alembic
```

### **Step 2: Database Setup**

```bash
# Using DBngin (Much simpler!)

# 1. Open DBngin app
# 2. Create new PostgreSQL server:
#    - Version: PostgreSQL 15+
#    - Port: 5432 (default) or custom
#    - Name: CFTeam-Ecosystem

# 3. Create database via DBngin GUI or command line:
createdb -h localhost -p 5432 crewai_ecosystem

# 4. For Redis, add Redis server in DBngin:
#    - Version: Redis 7+
#    - Port: 6379 (default)
#    - Name: CFTeam-Redis

# Alternative: Redis via Homebrew if not in DBngin
# brew install redis
# brew services start redis
```

### **Step 3: Configuration Files**

```bash
```bash
# Environment configuration for DBngin
cat > .env << 'EOF'
# Database Configuration (DBngin PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=crewai_ecosystem
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password

# Redis Configuration (DBngin Redis or local)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Project Paths
BURROW_HUB_PATH=/Users/andreagroferreira/Herd/burrowhub
ECOMMERCE_PATH=/Users/andreagroferreira/Work/ecommerce
FLOWNETWORK_PATH=/Users/andreagroferreira/Herd/flownetwork-integration-ms
GOBLINLEDGER_PATH=/Users/andreagroferreira/Herd/goblinledger

# MCP Configuration
CONTEXT7_ENABLED=true
NOTION_ENABLED=true
SUPABASE_ENABLED=true

# CrewAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
CREWAI_TELEMETRY_OPT_OUT=true

# Notification Configuration
WEBHOOK_URL=
SLACK_WEBHOOK=
DISCORD_WEBHOOK=
EOF
```

### **Step 4: Run Setup Script**

```python
# src/main.py
"""
CFTeam - CrewAI Multi-Project Development Ecosystem
Entry point for the agent coordination system
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from config.database import init_database
from config.redis_config import init_redis
from services.session_manager import SessionManager
from services.task_coordinator import TaskCoordinator
from cli.commands import CLIHandler
from crews.management_crew import ManagementCrew
from crews.backend_crew import BackendCrew
from crews.frontend_crew import FrontendCrew
from crews.integration_crew import IntegrationCrew
from crews.quality_crew import QualityCrew
from crews.intelligence_crew import IntelligenceCrew

# Load environment variables
load_dotenv()

class CFTeamOrchestrator:
    """Main orchestrator for the CrewAI ecosystem"""
    
    def __init__(self):
        self.session_manager = None
        self.task_coordinator = None
        self.crews = {}
        self.cli_handler = None
    
    async def initialize(self):
        """Initialize all system components"""
        print("🚀 Initializing CFTeam CrewAI Ecosystem...")
        
        # Initialize database connections
        await init_database()
        await init_redis()
        
        # Initialize core services
        self.session_manager = SessionManager()
        self.task_coordinator = TaskCoordinator()
        
        # Initialize crews
        await self._initialize_crews()
        
        # Initialize CLI handler
        self.cli_handler = CLIHandler(self)
        
        print("✅ CFTeam ecosystem initialized successfully!")
    
    async def _initialize_crews(self):
        """Initialize all crews with their agents"""
        self.crews = {
            'management': ManagementCrew(),
            'backend': BackendCrew(),
            'frontend': FrontendCrew(),
            'integration': IntegrationCrew(),
            'quality': QualityCrew(),
            'intelligence': IntelligenceCrew()
        }
        
        # Initialize each crew
        for name, crew in self.crews.items():
            await crew.initialize()
            print(f"✅ {name.title()} crew initialized")
    
    async def start_interactive_session(self):
        """Start interactive CLI session"""
        print("\n🎯 CFTeam Interactive Session Started")
        print("Type 'help' for available commands or 'quit' to exit")
        
        try:
            await self.cli_handler.start_interactive_mode()
        except KeyboardInterrupt:
            print("\n👋 Session ended by user")
        except Exception as e:
            print(f"❌ Session error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up resources...")
        # Close database connections, Redis connections, etc.
        
async def main():
    """Main entry point"""
    orchestrator = CFTeamOrchestrator()
    await orchestrator.initialize()
    await orchestrator.start_interactive_session()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🏃 **COMMON DEVELOPMENT COMMANDS**

### **Quick Start**
```bash
# Activate environment and start CFTeam
cd /Users/andreagroferreira/Work/CFTeam
source venv/bin/activate
python src/main.py

# Or use the alias after setup
cfteam
```

### **Testing Commands**
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_agents.py

# Run with coverage
python -m pytest --cov=src tests/

# Run tests in verbose mode
python -m pytest -v tests/
```

### **Code Quality**
```bash
# Format code with Black
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all quality checks
make quality  # If Makefile exists
```

### **Database Management**
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### **Development Workflow**
```bash
# Install new dependency
pip install package_name
pip freeze > requirements.txt

# Update all dependencies
pip install --upgrade -r requirements.txt

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## 📋 **KEY ARCHITECTURE CONCEPTS**

### **agents.yaml - Agent Definitions**

```yaml
# Management Tier Agents
technical_director:
  role: "Technical Director"
  goal: "Ensure architectural excellence and technical standards across all projects"
  backstory: "Senior architect with 15+ years experience in Laravel, Vue.js, and enterprise systems"
  capabilities:
    - architecture_review
    - technical_decision_making
    - cross_project_coordination
    - standard_enforcement
  max_rpm: 20
  allow_delegation: true

project_manager:
  role: "Project Manager"
  goal: "Coordinate development activities and ensure timely delivery"
  backstory: "Experienced PM specializing in multi-project coordination and agile methodologies"
  capabilities:
    - sprint_planning
    - progress_tracking
    - dependency_management
    - stakeholder_communication
  max_rpm: 30
  allow_delegation: true

qa_manager:
  role: "Quality Assurance Manager"
  goal: "Maintain high code quality and testing standards across all projects"
  backstory: "QA expert with deep knowledge of Laravel testing, Vue.js testing, and CI/CD"
  capabilities:
    - quality_strategy
    - test_coordination
    - code_review_oversight
    - compliance_validation
  max_rpm: 25
  allow_delegation: true

# Development Agents
laravel_architect:
  role: "Laravel Architect"
  goal: "Design and implement Laravel backend solutions following best practices"
  backstory: "Laravel expert specializing in modular architecture, Action patterns, and API design"
  capabilities:
    - laravel_architecture
    - api_design
    - module_creation
    - database_design
  tools:
    - laravel_artisan
    - composer_manager
    - phpstan_analyzer
  max_rpm: 15

vue_architect:
  role: "Vue.js Architect" 
  goal: "Create efficient Vue.js interfaces with TypeScript and Vuetify"
  backstory: "Frontend expert in Vue 3, TypeScript, Vuetify 3, and modern development practices"
  capabilities:
    - vue_architecture
    - component_design
    - state_management
    - typescript_implementation
  tools:
    - vue_cli
    - vite_builder
    - typescript_checker
  max_rpm: 15

# Intelligence Agents
context_seven:
  role: "Documentation Intelligence"
  goal: "Provide accurate technical guidance from Context7 documentation"
  backstory: "AI assistant specialized in Laravel, Vue.js, and modern web development documentation"
  capabilities:
    - documentation_search
    - pattern_validation
    - best_practice_guidance
    - knowledge_synthesis
  tools:
    - context7_mcp
  max_rpm: 50

notion_manager:
  role: "Project Information Manager"
  goal: "Maintain project documentation and coordinate task management via Notion"
  backstory: "Information management specialist focused on cross-project coordination"
  capabilities:
    - notion_integration
    - task_synchronization
    - progress_reporting
    - documentation_management
  tools:
    - notion_mcp
  max_rpm: 40

supabase_intelligence:
  role: "Data Intelligence Analyst"
  goal: "Analyze production data to inform development decisions"
  backstory: "Data analyst with expertise in production systems and business intelligence"
  capabilities:
    - data_analysis
    - schema_validation
    - performance_insights
    - business_intelligence
  tools:
    - supabase_mcp
  max_rpm: 30
```

### **crews.yaml - Crew Configurations**

```yaml
management_crew:
  name: "Management & Coordination"
  description: "Strategic oversight and cross-project coordination"
  agents:
    - technical_director
    - project_manager
    - qa_manager
  process: hierarchical
  manager_agent: technical_director
  verbose: true

backend_development_crew:
  name: "Backend Development"
  description: "Laravel backend development and API design"
  agents:
    - laravel_architect
    - module_builder
    - api_designer
    - database_architect
  process: sequential
  verbose: true

frontend_development_crew:
  name: "Frontend Development"
  description: "Vue.js frontend development and user interface"
  agents:
    - vue_architect
    - component_builder
    - page_builder
    - typescript_validator
  process: sequential
  verbose: true

integration_crew:
  name: "Cross-Project Integration"
  description: "Multi-project coordination and data synchronization"
  agents:
    - integration_manager
    - cross_project_sync
    - payment_gateway
    - data_consistency
  process: parallel
  verbose: true

quality_assurance_crew:
  name: "Quality Assurance"
  description: "Code quality, testing, and compliance validation"
  agents:
    - code_quality_lead
    - phpstan_validator
    - pint_formatter
    - test_runner
  process: sequential
  verbose: true

intelligence_crew:
  name: "Knowledge & Data Intelligence"
  description: "Documentation, data analysis, and information management"
  agents:
    - context_seven
    - notion_manager
    - supabase_intelligence
  process: parallel
  verbose: true
```

### **projects.yaml - Project Configurations**

```yaml
projects:
  burrow_hub:
    name: "Burrow Hub CRM"
    path: "/Users/andreagroferreira/Herd/burrowhub"
    type: "laravel"
    database: "supabase"
    primary_crews:
      - backend_development_crew
      - management_crew
      - quality_assurance_crew
    
  ecommerce:
    name: "E-commerce Frontend"
    path: "/Users/andreagroferreira/Work/ecommerce"
    type: "nuxt"
    database: "api_driven"
    primary_crews:
      - frontend_development_crew
      - integration_crew
    
  flownetwork:
    name: "FlowNetwork Integration MS"
    path: "/Users/andreagroferreira/Herd/flownetwork-integration-ms"
    type: "laravel"
    database: "postgresql"
    primary_crews:
      - backend_development_crew
      - integration_crew
    
  goblinledger:
    name: "GoblinLedger Primavera MS"
    path: "/Users/andreagroferreira/Herd/goblinledger"
    type: "laravel"
    database: "postgresql"
    primary_crews:
      - backend_development_crew
      - integration_crew

ecosystem:
  coordination_database: "postgresql"
  communication_layer: "redis"
  session_persistence: true
  cross_project_sync: true
  git_coordination: true
```

---

## 🎛️ **CFTEAM CLI COMMANDS**

### **Session Management**
```bash
# Start new development session
cfteam start-session "payment-gateway-optimization" --projects=burrow-hub,ecommerce --priority=urgent

# Join existing session
cfteam join-session <session-id> --project=ecommerce

# View active sessions
cfteam sessions --active

# End session
cfteam end-session <session-id> --with-summary
```

### **Development Commands**
```bash
# Create Laravel module (Backend Crew)
cfteam create-module "PaymentGateway" --project=burrow-hub --with-tests

# Create Vue page (Frontend Crew)
cfteam create-page "PaymentOptimization" --project=ecommerce --module=checkout

# Create API endpoint (Integration Crew)
cfteam create-api "payment-gateways/optimize" --project=burrow-hub --method=post

# Fix critical issue (All relevant crews)
cfteam urgent-fix "klarna-post-endpoint" --auto-coordinate
```

### **Quality Assurance Commands**
```bash
# Run quality checks (Quality Crew)
cfteam quality-check --projects=all --include=phpstan,pint,tests

# Cross-project validation (Integration Crew)
cfteam validate-integration --source=burrow-hub --targets=ecommerce,flownetwork

# Security scan (Quality Crew)
cfteam security-scan --projects=all --severity=high
```

### **Intelligence Commands**
```bash
# Query documentation (Intelligence Crew)
cfteam ask-context7 "Laravel 11 best practices for payment controllers"

# Sync with Notion (Intelligence Crew)
cfteam sync-notion --pages=all --bidirectional

# Analyze production data (Intelligence Crew)
cfteam analyze-data "payment success rates last 30 days" --supabase
```

### **Coordination Commands**
```bash
# Cross-project deployment
cfteam deploy --projects=burrow-hub,ecommerce --coordinate --with-rollback

# Git coordination
cfteam git-checkpoint "pre-payment-optimization" --all-projects

# Status overview
cfteam status --dashboard --live

# Emergency coordination
cfteam emergency-response "production payment failure" --all-hands
```

---

## 🔧 **SERVICE MANAGEMENT**

### **Start Services**
```bash
# Using DBngin GUI
# 1. Open DBngin app
# 2. Start PostgreSQL server (CFTeam-Ecosystem)
# 3. Start Redis server (CFTeam-Redis)

# Or via command line if using local services
brew services start postgresql@15
brew services start redis
```

### **Stop Services**
```bash
# Stop via DBngin GUI or:
brew services stop postgresql@15
brew services stop redis
```

### **Service Health Checks**
```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping

# Check all CFTeam services
cfteam health-check --all
```

---

## 📜 **SETUP SCRIPTS**

### **setup_environment.sh**
```bash
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
from config.database import init_database, create_tables
asyncio.run(init_database())
asyncio.run(create_tables())
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
```

---

## 📊 **MONITORING & DEBUGGING**

### **Log Access**
```bash
# View real-time logs
tail -f logs/cfteam.log

# View specific crew logs
tail -f logs/backend_crew.log

# Search logs for errors
grep ERROR logs/*.log

# View agent communication logs
cfteam logs --agents --follow
```

### **Debug Mode**
```bash
# Run in debug mode
CFTEAM_DEBUG=true cfteam

# Enable verbose CrewAI output
export CREWAI_VERBOSE=true

# Debug specific crew
cfteam debug-crew backend_development_crew
```

### **Environment Variables**
```bash
# Critical environment variables that must be set:
OPENAI_API_KEY      # Required for CrewAI agents
POSTGRES_HOST       # DBngin PostgreSQL host
POSTGRES_PORT       # DBngin PostgreSQL port
POSTGRES_DB         # Database name (crewai_ecosystem)
POSTGRES_USER       # PostgreSQL username
POSTGRES_PASSWORD   # PostgreSQL password
REDIS_HOST          # Redis host (localhost)
REDIS_PORT          # Redis port (6379)
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

### **Database Connection Issues**
```bash
# Check DBngin PostgreSQL server status
# Open DBngin app and verify PostgreSQL is running

# Test connection manually
psql -h localhost -p 5432 -U your_username -d crewai_ecosystem

# If database doesn't exist, create it:
createdb -h localhost -p 5432 -U your_username crewai_ecosystem
```

#### **Redis Connection Issues**
```bash
# Check DBngin Redis server status 
# Open DBngin app and verify Redis is running

# Test connection manually
redis-cli -h localhost -p 6379 ping

# If Redis not in DBngin, install via Homebrew:
brew install redis
brew services start redis
```

#### **Agent Communication Issues**
```bash
# Check agent status
cfteam status --agents --detailed

# Reset ecosystem state
cfteam reset-ecosystem --confirm

# Restart specific crew
cfteam restart-crew backend_development_crew
```

### **Performance Optimization**
```bash
# Monitor resource usage
cfteam performance --cpu --memory --database

# Optimize agent RPM limits
cfteam configure-agents --optimize-rpm --based-on-usage

# Clear cache and queues
cfteam maintenance --clear-cache --reset-queues
```

---

## 📝 **IMPORTANT DEVELOPMENT NOTES**

### **Project Status**
- This is a greenfield project - all code needs to be implemented from scratch
- The CLAUDE.md serves as the complete specification and implementation guide
- Follow the exact structure and patterns defined in this document

### **Implementation Priority**
1. Core infrastructure (database, Redis, configuration)
2. Base agent and crew classes
3. CLI framework and commands
4. Individual agents implementation
5. Workflow orchestration
6. Testing and quality assurance

### **Key Design Principles**
- **Modular Architecture**: Each agent is independent and communicates via standardized interfaces
- **Async-First**: All operations should be asynchronous for optimal performance
- **Error Resilience**: Agents should handle failures gracefully without crashing the ecosystem
- **Observability**: Comprehensive logging and monitoring throughout the system

### **MCP Integration Notes**
- Context7 MCP for documentation intelligence
- Notion MCP for project management sync
- Supabase MCP for production data analysis
- All MCPs should be configured in Claude Code settings before use

### **Development Workflow Rules**
- **IMPORTANT**: Create a git commit after completing each task/todo item
- Use descriptive commit messages that explain what was implemented
- Group related small changes in a single commit
- Never commit broken or incomplete code