"""
YAML Configuration Loader for CFTeam ecosystem
Loads and manages configurations from YAML files
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel, ValidationError

from src.config import get_logger
from src.models import ProjectType, ProjectStatus
from src.agents.base_agent import AgentConfig
from src.crews.base_crew import CrewConfig, CrewProcess


class YAMLConfigLoader:
    """Loads and manages YAML configurations"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.logger = get_logger(__name__)
        self.config_dir = config_dir or Path(__file__).parent
        
        # Loaded configurations
        self.agents_config: Dict[str, Dict[str, Any]] = {}
        self.crews_config: Dict[str, Dict[str, Any]] = {}
        self.projects_config: Dict[str, Dict[str, Any]] = {}
        self.ecosystem_config: Dict[str, Any] = {}
        
        # Load all configurations
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all YAML configuration files"""
        try:
            self.agents_config = self.load_yaml_file("agents.yaml")
            self.logger.info(f"Loaded {len(self.agents_config)} agent configurations")
            
            self.crews_config = self.load_yaml_file("crews.yaml")
            self.logger.info(f"Loaded {len(self.crews_config)} crew configurations")
            
            projects_data = self.load_yaml_file("projects.yaml")
            self.projects_config = projects_data.get("projects", {})
            self.ecosystem_config = projects_data.get("ecosystem", {})
            self.logger.info(f"Loaded {len(self.projects_config)} project configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load configurations: {e}")
            raise
    
    def load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file"""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                return data or {}
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file {filename}: {e}")
            raise
    
    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent"""
        return self.agents_config.get(agent_id)
    
    def get_crew_config(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific crew"""
        return self.crews_config.get(crew_id)
    
    def get_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific project"""
        return self.projects_config.get(project_id)
    
    def list_agents(self) -> List[str]:
        """List all available agent IDs"""
        return list(self.agents_config.keys())
    
    def list_crews(self) -> List[str]:
        """List all available crew IDs"""
        return list(self.crews_config.keys())
    
    def list_projects(self) -> List[str]:
        """List all available project IDs"""
        return list(self.projects_config.keys())
    
    def create_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Create AgentConfig from YAML data"""
        data = self.get_agent_config(agent_id)
        if not data:
            return None
        
        try:
            # Map YAML data to AgentConfig
            from src.models import AgentRole, AgentTier
            
            # Determine tier from agent_id patterns
            tier = AgentTier.MANAGEMENT
            if agent_id in ["technical_director", "project_manager", "qa_manager"]:
                tier = AgentTier.MANAGEMENT
            elif agent_id in ["laravel_architect", "vue_architect", "module_builder", "api_designer", "payment_gateway"]:
                tier = AgentTier.DEVELOPMENT
            elif agent_id in ["code_quality_lead", "phpstan_validator", "pint_formatter", "test_runner"]:
                tier = AgentTier.QUALITY
            elif agent_id in ["context_seven", "notion_manager", "supabase_intelligence"]:
                tier = AgentTier.INTELLIGENCE
            elif agent_id in ["cross_project_sync", "data_consistency", "deployment_manager"]:
                tier = AgentTier.INTEGRATION
            
            config = AgentConfig(
                identifier=agent_id,
                name=data.get("role", agent_id),
                role=AgentRole[agent_id.upper()],
                tier=tier,
                goal=data.get("goal", ""),
                backstory=data.get("backstory", ""),
                capabilities=data.get("capabilities", []),
                tools=data.get("tools", []),
                max_rpm=data.get("max_rpm", 20),
                allow_delegation=data.get("allow_delegation", False),
                can_manage_crew=data.get("allow_delegation", False),
            )
            
            return config
            
        except (KeyError, ValidationError) as e:
            self.logger.error(f"Failed to create AgentConfig for {agent_id}: {e}")
            return None
    
    def create_crew_config(self, crew_id: str) -> Optional[CrewConfig]:
        """Create CrewConfig from YAML data"""
        data = self.get_crew_config(crew_id)
        if not data:
            return None
        
        try:
            # Map process string to enum
            process_map = {
                "sequential": CrewProcess.SEQUENTIAL,
                "hierarchical": CrewProcess.HIERARCHICAL,
                "parallel": CrewProcess.PARALLEL,
            }
            
            config = CrewConfig(
                name=data.get("name", crew_id),
                description=data.get("description", ""),
                agents=data.get("agents", []),
                process=process_map.get(data.get("process", "sequential"), CrewProcess.SEQUENTIAL),
                manager_agent=data.get("manager_agent"),
                verbose=data.get("verbose", True),
                memory=data.get("memory", True),
                planning=data.get("planning", False),
                responsibilities=data.get("responsibilities", []),
            )
            
            return config
            
        except ValidationError as e:
            self.logger.error(f"Failed to create CrewConfig for {crew_id}: {e}")
            return None
    
    def create_project_dict(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Create project dictionary from YAML data"""
        data = self.get_project_config(project_id)
        if not data:
            return None
        
        try:
            # Map string values to enums
            project_type_map = {
                "laravel": ProjectType.LARAVEL,
                "nuxt": ProjectType.NUXT,
                "vue": ProjectType.VUE,
                "microservice": ProjectType.MICROSERVICE,
                "api": ProjectType.API,
            }
            
            status_map = {
                "active": ProjectStatus.ACTIVE,
                "maintenance": ProjectStatus.MAINTENANCE,
                "development": ProjectStatus.DEVELOPMENT,
                "archived": ProjectStatus.ARCHIVED,
                "paused": ProjectStatus.PAUSED,
            }
            
            project_dict = {
                "identifier": project_id,
                "name": data.get("name", project_id),
                "description": data.get("description", ""),
                "project_type": project_type_map.get(data.get("type", "other"), ProjectType.OTHER),
                "status": status_map.get(data.get("status", "active"), ProjectStatus.ACTIVE),
                "path": data.get("path", ""),
                "repository_url": data.get("repository", {}).get("url", ""),
                "database_type": data.get("database", {}).get("type", ""),
                "primary_language": data.get("technology", {}).get("primary_language", ""),
                "framework_version": data.get("technology", {}).get("framework", ""),
                "dependencies": data.get("dependencies", {}),
                "primary_crews": data.get("primary_crews", []),
                "build_commands": data.get("build_commands", {}),
                "quality_thresholds": data.get("quality_thresholds", {}),
                "integrations": data.get("integrations", []),
            }
            
            return project_dict
            
        except Exception as e:
            self.logger.error(f"Failed to create project dict for {project_id}: {e}")
            return None
    
    def reload_configs(self):
        """Reload all configuration files"""
        self.logger.info("Reloading all configuration files...")
        self.load_all_configs()


# Global configuration loader instance
config_loader = YAMLConfigLoader()


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get agent configuration"""
    return config_loader.create_agent_config(agent_id)


def get_crew_config(crew_id: str) -> Optional[CrewConfig]:
    """Get crew configuration"""
    return config_loader.create_crew_config(crew_id)


def get_project_config(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project configuration"""
    return config_loader.create_project_dict(project_id)


def list_available_agents() -> List[str]:
    """List available agent IDs"""
    return config_loader.list_agents()


def list_available_crews() -> List[str]:
    """List available crew IDs"""
    return config_loader.list_crews()


def list_available_projects() -> List[str]:
    """List available project IDs"""
    return config_loader.list_projects()