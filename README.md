# 🤖 CFTeam - CrewAI Multi-Project Development Ecosystem

Advanced AI agent ecosystem for coordinated development across Laravel CRM/E-commerce projects using CrewAI, PostgreSQL, Redis, and MCPs integration.

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/andreagroferreira/cfteam.git
   cd cfteam
   ```

2. **Copy environment template**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   ```

3. **Run setup script**
   ```bash
   chmod +x scripts/setup_environment.sh
   ./scripts/setup_environment.sh
   ```

4. **Start the ecosystem**
   ```bash
   source ~/.zshrc
   cfteam
   ```

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 15+ (via DBngin or local)
- Redis 7+ (via DBngin or local)
- OpenAI API key

## 🏗️ Architecture

The CFTeam ecosystem manages multiple interconnected projects:

- **Burrow Hub CRM** - Laravel-based CRM system
- **E-commerce Frontend** - Nuxt.js storefront
- **FlowNetwork MS** - Integration microservice
- **GoblinLedger MS** - Financial microservice

## 🤖 Agent Hierarchy

1. **Management Tier** - Strategic oversight and coordination
2. **Development Tier** - Implementation and coding
3. **Intelligence Tier** - Documentation and data analysis
4. **Integration Tier** - Cross-project synchronization
5. **Quality Tier** - Testing and code standards

## 📚 Documentation

For detailed documentation, see the [CLAUDE.md](CLAUDE.md) file which contains:
- Complete project structure
- Agent specifications
- CLI commands reference
- Configuration details
- Troubleshooting guide

## 🔧 Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Code quality checks
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📄 License

MIT License - see LICENSE file for details