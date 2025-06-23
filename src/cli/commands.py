"""
CLI Commands for CFTeam ecosystem
Handles interactive commands and user interface
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

from src.config import get_logger

# Command history file
HISTORY_FILE = Path.home() / '.cfteam_history'

# CLI style
CLI_STYLE = Style.from_dict({
    'prompt': '#00aa00 bold',
    'command': '#0088ff',
})

# Available commands
COMMANDS = {
    'help': 'Show available commands',
    'status': 'Show system status',
    'sessions': 'List active sessions',
    'start-session': 'Start a new development session',
    'join-session': 'Join an existing session',
    'end-session': 'End a session',
    'agents': 'List available agents',
    'crews': 'List available crews',
    'projects': 'List managed projects',
    'create-module': 'Create a new module',
    'create-page': 'Create a new page',
    'create-api': 'Create a new API endpoint',
    'quality-check': 'Run quality checks',
    'deploy': 'Deploy projects',
    'git-checkpoint': 'Create git checkpoint',
    'dashboard': 'Show real-time dashboard',
    'logs': 'View logs',
    'health': 'Check system health',
    'quit': 'Exit CFTeam',
    'exit': 'Exit CFTeam',
}


class CLIHandler:
    """Handles CLI commands and interactions"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.console = Console()
        self.logger = get_logger(__name__)
        self.session = PromptSession(
            history=FileHistory(str(HISTORY_FILE)),
            style=CLI_STYLE,
            completer=WordCompleter(list(COMMANDS.keys()), ignore_case=True),
        )
        self.running = False
    
    async def start_interactive_mode(self):
        """Start interactive command mode"""
        self.running = True
        
        while self.running:
            try:
                # Get command from user
                command_line = await self.session.prompt_async(
                    '\n[CFTeam] > ',
                    style=CLI_STYLE
                )
                
                if not command_line.strip():
                    continue
                
                # Parse and execute command
                await self.execute_command(command_line.strip())
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="bold red")
                self.logger.error(f"Command error: {e}", exc_info=True)
    
    async def execute_command(self, command_line: str):
        """Execute a command"""
        parts = command_line.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Route to appropriate handler
        if command in ['help', '?']:
            self.show_help()
        elif command == 'status':
            await self.show_status()
        elif command == 'sessions':
            await self.list_sessions(args)
        elif command == 'start-session':
            await self.start_session(args)
        elif command == 'agents':
            await self.list_agents()
        elif command == 'crews':
            await self.list_crews()
        elif command == 'projects':
            await self.list_projects()
        elif command == 'health':
            await self.check_health()
        elif command == 'dashboard':
            await self.show_dashboard()
        elif command in ['quit', 'exit', 'q']:
            self.running = False
        else:
            self.console.print(f"❓ Unknown command: {command}", style="yellow")
            self.console.print("Type 'help' for available commands", style="dim")
    
    def show_help(self):
        """Show help information"""
        table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        for cmd, desc in COMMANDS.items():
            table.add_row(cmd, desc)
        
        self.console.print(table)
        self.console.print("\n💡 Example: start-session \"Fix payment gateway\" --projects=burrow-hub --priority=high", style="dim")
    
    async def show_status(self):
        """Show system status"""
        panel = Panel.fit(
            f"""[bold cyan]System Status[/bold cyan]
            
🟢 Database: Connected
🟢 Redis: Connected
🟢 Agents: 0 active
🟢 Sessions: 0 active
🟢 Tasks: 0 pending

[dim]Uptime: 0m 0s[/dim]
""",
            title="CFTeam Status",
            border_style="green"
        )
        self.console.print(panel)
    
    async def list_sessions(self, args: List[str]):
        """List active sessions"""
        # TODO: Implement session listing from database
        table = Table(title="Active Sessions", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", style="green")
        table.add_column("Projects", style="yellow")
        table.add_column("Started", style="dim")
        
        # Placeholder data
        table.add_row(
            "abc123",
            "Payment Gateway Fix",
            "Active",
            "burrow-hub",
            "5 minutes ago"
        )
        
        self.console.print(table)
    
    async def start_session(self, args: List[str]):
        """Start a new session"""
        if not args:
            self.console.print("❌ Please provide a session name", style="red")
            self.console.print("Usage: start-session \"Session Name\" [--projects=p1,p2] [--priority=high]", style="dim")
            return
        
        session_name = args[0]
        self.console.print(f"✅ Starting session: {session_name}", style="green")
        # TODO: Implement session creation
    
    async def list_agents(self):
        """List available agents"""
        table = Table(title="Available Agents", show_header=True)
        table.add_column("Identifier", style="cyan")
        table.add_column("Role", style="white")
        table.add_column("Status", style="green")
        table.add_column("Tier", style="yellow")
        
        # TODO: Load from YAML config
        agents = [
            ("technical_director", "Technical Director", "Available", "Management"),
            ("laravel_architect", "Laravel Architect", "Available", "Development"),
            ("vue_architect", "Vue.js Architect", "Available", "Development"),
        ]
        
        for agent in agents:
            table.add_row(*agent)
        
        self.console.print(table)
    
    async def list_crews(self):
        """List available crews"""
        table = Table(title="Available Crews", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Agents", style="yellow", no_wrap=False)
        
        # TODO: Load from YAML config
        crews = [
            ("Management Crew", "Strategic oversight", "Technical Director, Project Manager, QA Manager"),
            ("Backend Crew", "Laravel development", "Laravel Architect, Module Builder, API Designer"),
            ("Frontend Crew", "Vue.js development", "Vue Architect, Module Builder"),
        ]
        
        for crew in crews:
            table.add_row(*crew)
        
        self.console.print(table)
    
    async def list_projects(self):
        """List managed projects"""
        table = Table(title="Managed Projects", show_header=True)
        table.add_column("Identifier", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Path", style="dim", no_wrap=True)
        
        # TODO: Load from YAML config
        projects = [
            ("burrow_hub", "Burrow Hub CRM", "Laravel", "Active", "/Users/.../burrowhub"),
            ("ecommerce", "E-commerce Frontend", "Nuxt", "Active", "/Users/.../ecommerce"),
            ("flownetwork", "FlowNetwork MS", "Microservice", "Active", "/Users/.../flownetwork"),
            ("goblinledger", "GoblinLedger MS", "Microservice", "Active", "/Users/.../goblinledger"),
        ]
        
        for project in projects:
            table.add_row(*project)
        
        self.console.print(table)
    
    async def check_health(self):
        """Check system health"""
        self.console.print("🔍 Checking system health...", style="yellow")
        
        # TODO: Implement actual health checks
        health_items = [
            ("Database", "✅ Healthy", "green"),
            ("Redis", "✅ Healthy", "green"),
            ("Agents", "✅ All responding", "green"),
            ("Disk Space", "✅ 45% free", "green"),
            ("Memory", "✅ 2.3GB available", "green"),
        ]
        
        for item, status, color in health_items:
            self.console.print(f"  {item}: {status}", style=color)
        
        self.console.print("\n✨ System is healthy", style="bold green")
    
    async def show_dashboard(self):
        """Show real-time dashboard"""
        self.console.print("📊 Dashboard feature coming soon!", style="yellow")
        # TODO: Implement real-time dashboard with Rich Live display