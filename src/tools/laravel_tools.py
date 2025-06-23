"""
Laravel-specific tools for CrewAI agents
"""

import subprocess
import os
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool


class ArtisanTool(BaseTool):
    name: str = "artisan"
    description: str = "Execute Laravel Artisan commands"
    
    def _run(self, project_path: str, command: str, args: Optional[List[str]] = None) -> str:
        """Execute artisan command"""
        try:
            cmd = ["php", "artisan", command]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Artisan command failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing artisan: {str(e)}"


class ComposerTool(BaseTool):
    name: str = "composer"
    description: str = "Execute Composer commands"
    
    def _run(self, project_path: str, command: str, args: Optional[List[str]] = None) -> str:
        """Execute composer command"""
        try:
            cmd = ["composer", command]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Composer command failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing composer: {str(e)}"


class PHPStanTool(BaseTool):
    name: str = "phpstan"
    description: str = "Run PHPStan static analysis"
    
    def _run(self, project_path: str, paths: Optional[List[str]] = None, level: int = 5) -> str:
        """Execute PHPStan analysis"""
        try:
            cmd = ["./vendor/bin/phpstan", "analyse", f"--level={level}"]
            
            if paths:
                cmd.extend(paths)
            else:
                cmd.extend(["app", "database", "routes"])
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            return result.stdout
            
        except Exception as e:
            return f"Error executing PHPStan: {str(e)}"


class PintTool(BaseTool):
    name: str = "pint"
    description: str = "Run Laravel Pint code formatter"
    
    def _run(self, project_path: str, paths: Optional[List[str]] = None, fix: bool = True) -> str:
        """Execute Pint formatter"""
        try:
            cmd = ["./vendor/bin/pint"]
            
            if not fix:
                cmd.append("--test")
            
            if paths:
                cmd.extend(paths)
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "Code formatting successful" if fix else "Code formatting check passed"
            else:
                return f"Pint failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing Pint: {str(e)}"


class PestTool(BaseTool):
    name: str = "pest"
    description: str = "Run Pest tests"
    
    def _run(self, project_path: str, filter: Optional[str] = None, coverage: bool = False) -> str:
        """Execute Pest tests"""
        try:
            cmd = ["./vendor/bin/pest"]
            
            if filter:
                cmd.extend(["--filter", filter])
            
            if coverage:
                cmd.append("--coverage")
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            return result.stdout
            
        except Exception as e:
            return f"Error executing Pest: {str(e)}"