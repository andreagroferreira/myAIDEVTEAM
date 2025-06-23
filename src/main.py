"""
CFTeam - CrewAI Multi-Project Development Ecosystem
Entry point for the agent coordination system
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    init_database, 
    init_redis, 
    close_database, 
    close_redis,
    setup_logging,
    get_logger
)
from src.services.session_manager import SessionManager
from src.services.task_coordinator import TaskCoordinator
from src.cli.commands import CLIHandler

# Load environment variables
load_dotenv()

# Initialize console and logger
console = Console()
logger = get_logger(__name__)


class CFTeamOrchestrator:
    """Main orchestrator for the CrewAI ecosystem"""
    
    def __init__(self):
        self.session_manager: Optional[SessionManager] = None
        self.task_coordinator: Optional[TaskCoordinator] = None
        self.crews = {}
        self.cli_handler: Optional[CLIHandler] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            console.print("\n=€ Initializing CFTeam CrewAI Ecosystem...\n", style="bold blue")
            
            # Initialize database connections
            console.print("=Ê Connecting to PostgreSQL...", style="yellow")
            await init_database()
            console.print(" Database connected", style="green")
            
            # Initialize Redis
            console.print("= Connecting to Redis...", style="yellow")
            await init_redis()
            console.print(" Redis connected", style="green")
            
            # Initialize core services
            console.print("=à  Initializing services...", style="yellow")
            self.session_manager = SessionManager()
            self.task_coordinator = TaskCoordinator()
            await self.session_manager.initialize()
            await self.task_coordinator.initialize()
            console.print(" Services initialized", style="green")
            
            # Initialize crews (placeholder for now)
            console.print("=e Loading crews...", style="yellow")
            await self._initialize_crews()
            console.print(" Crews loaded", style="green")
            
            # Initialize CLI handler
            self.cli_handler = CLIHandler(self)
            
            self.is_initialized = True
            console.print("\n( CFTeam ecosystem initialized successfully!\n", style="bold green")
            
        except Exception as e:
            console.print(f"\nL Initialization failed: {e}\n", style="bold red")
            logger.error(f"Failed to initialize CFTeam: {e}", exc_info=True)
            raise
    
    async def _initialize_crews(self):
        """Initialize all crews with their agents"""
        # TODO: Implement crew initialization from YAML configs
        pass
    
    async def start_interactive_session(self):
        """Start interactive CLI session"""
        welcome_text = Text()
        welcome_text.append("CFTeam Interactive Session\n", style="bold cyan")
        welcome_text.append("Type ", style="white")
        welcome_text.append("help", style="bold yellow")
        welcome_text.append(" for available commands or ", style="white")
        welcome_text.append("quit", style="bold yellow")
        welcome_text.append(" to exit", style="white")
        
        panel = Panel(
            welcome_text,
            title="> Welcome to CFTeam",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)
        
        try:
            if self.cli_handler:
                await self.cli_handler.start_interactive_mode()
        except KeyboardInterrupt:
            console.print("\n\n=K Session ended by user\n", style="yellow")
        except Exception as e:
            console.print(f"\nL Session error: {e}\n", style="bold red")
            logger.error(f"Session error: {e}", exc_info=True)
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        console.print("\n>ù Cleaning up resources...", style="yellow")
        
        try:
            # Cleanup services
            if self.session_manager:
                await self.session_manager.shutdown()
            if self.task_coordinator:
                await self.task_coordinator.shutdown()
            
            # Close database connections
            await close_database()
            await close_redis()
            
            console.print(" Cleanup complete\n", style="green")
            
        except Exception as e:
            console.print(f"   Cleanup warning: {e}", style="yellow")
            logger.warning(f"Cleanup warning: {e}")


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
def main(debug: bool, config: Optional[str]):
    """CFTeam - CrewAI Multi-Project Development Ecosystem"""
    
    # Set debug mode
    if debug:
        os.environ['DEBUG'] = 'true'
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Load custom config if provided
    if config:
        load_dotenv(config)
    
    # Run the async main function
    try:
        asyncio.run(async_main())
    except Exception as e:
        console.print(f"\nL Fatal error: {e}\n", style="bold red")
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


async def async_main():
    """Async main function"""
    orchestrator = CFTeamOrchestrator()
    
    try:
        await orchestrator.initialize()
        await orchestrator.start_interactive_session()
    except Exception as e:
        raise
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    main()