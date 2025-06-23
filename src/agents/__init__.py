"""
Agents module for CFTeam ecosystem
"""

from src.agents.base_agent import BaseAgent, AgentConfig
from src.agents.management import TechnicalDirector

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    
    # Management Agents
    "TechnicalDirector",
]