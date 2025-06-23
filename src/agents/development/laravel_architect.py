"""
Laravel Architect agent for CFTeam ecosystem
"""

from typing import Dict, Any, List, Optional
from crewai import Task

from src.agents.base_agent import BaseAgent, AgentConfig
from src.models import AgentRole, AgentTier
from src.tools.laravel_tools import ArtisanTool, ComposerTool


class LaravelArchitect(BaseAgent):
    """Laravel backend architect agent"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if not config:
            config = AgentConfig(
                identifier="laravel_architect",
                name="Laravel Architect",
                role=AgentRole.LARAVEL_ARCHITECT,
                tier=AgentTier.DEVELOPMENT,
                goal="Design and implement Laravel backend solutions following best practices",
                backstory="Laravel expert specializing in modular architecture, Action patterns, and API design",
                capabilities=[
                    "laravel_architecture",
                    "api_design",
                    "module_creation",
                    "database_design"
                ],
                tools=["artisan", "composer"],
                max_rpm=15,
                allow_delegation=False
            )
        
        super().__init__(config)
        
        # Initialize tools
        self.artisan_tool = ArtisanTool()
        self.composer_tool = ComposerTool()
    
    async def create_module(
        self,
        module_name: str,
        project_path: str,
        with_tests: bool = True
    ) -> Dict[str, Any]:
        """Create a new Laravel module"""
        self.logger.info(f"Creating Laravel module: {module_name}")
        
        try:
            # Create module structure
            commands = [
                f"make:module {module_name}",
                f"module:make-controller {module_name}Controller {module_name}",
                f"module:make-model {module_name} {module_name}",
                f"module:make-migration create_{module_name.lower()}_table {module_name}",
                f"module:make-seeder {module_name}Seeder {module_name}",
                f"module:make-action {module_name}/Store{module_name}Action {module_name}",
                f"module:make-action {module_name}/Update{module_name}Action {module_name}",
                f"module:make-action {module_name}/Delete{module_name}Action {module_name}",
                f"module:make-dto {module_name}Data {module_name}",
                f"module:make-request Store{module_name}Request {module_name}",
                f"module:make-request Update{module_name}Request {module_name}",
                f"module:make-resource {module_name}Resource {module_name}"
            ]
            
            if with_tests:
                commands.extend([
                    f"module:make-test {module_name}Test {module_name}",
                    f"module:make-test {module_name}ApiTest {module_name} --feature"
                ])
            
            results = []
            for cmd in commands:
                result = self.artisan_tool._run(project_path, cmd)
                results.append(result)
            
            return {
                'success': True,
                'module': module_name,
                'commands_executed': len(commands),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create module {module_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_api_endpoint(
        self,
        endpoint_name: str,
        module_name: str,
        project_path: str,
        methods: List[str] = None
    ) -> Dict[str, Any]:
        """Create API endpoint with controller and routes"""
        if not methods:
            methods = ["index", "show", "store", "update", "destroy"]
        
        self.logger.info(f"Creating API endpoint: {endpoint_name} for module {module_name}")
        
        try:
            # Create API controller
            result = self.artisan_tool._run(
                project_path,
                f"module:make-controller Api/{endpoint_name}Controller {module_name} --api"
            )
            
            # Generate route entries
            routes = []
            if "index" in methods:
                routes.append(f"Route::get('{endpoint_name.lower()}', [Api\\{endpoint_name}Controller::class, 'index']);")
            if "show" in methods:
                routes.append(f"Route::get('{endpoint_name.lower()}/{{id}}', [Api\\{endpoint_name}Controller::class, 'show']);")
            if "store" in methods:
                routes.append(f"Route::post('{endpoint_name.lower()}', [Api\\{endpoint_name}Controller::class, 'store']);")
            if "update" in methods:
                routes.append(f"Route::put('{endpoint_name.lower()}/{{id}}', [Api\\{endpoint_name}Controller::class, 'update']);")
            if "destroy" in methods:
                routes.append(f"Route::delete('{endpoint_name.lower()}/{{id}}', [Api\\{endpoint_name}Controller::class, 'destroy']);")
            
            return {
                'success': True,
                'endpoint': endpoint_name,
                'controller_created': result,
                'routes': routes
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create API endpoint {endpoint_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }