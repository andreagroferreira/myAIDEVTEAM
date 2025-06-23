"""
Vue.js-specific tools for CrewAI agents
"""

import subprocess
import os
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool


class NpmTool(BaseTool):
    name: str = "npm"
    description: str = "Execute npm commands"
    
    def _run(self, project_path: str, command: str, args: Optional[List[str]] = None) -> str:
        """Execute npm command"""
        try:
            cmd = ["npm", command]
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
                return f"npm command failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing npm: {str(e)}"


class ViteTool(BaseTool):
    name: str = "vite"
    description: str = "Execute Vite build commands"
    
    def _run(self, project_path: str, mode: str = "build") -> str:
        """Execute vite command"""
        try:
            if mode == "dev":
                cmd = ["npm", "run", "dev"]
            elif mode == "build":
                cmd = ["npm", "run", "build"]
            elif mode == "preview":
                cmd = ["npm", "run", "preview"]
            else:
                return f"Unknown mode: {mode}"
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Vite {mode} completed successfully"
            else:
                return f"Vite {mode} failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing vite: {str(e)}"


class TypeScriptTool(BaseTool):
    name: str = "typescript"
    description: str = "Run TypeScript type checking"
    
    def _run(self, project_path: str, watch: bool = False) -> str:
        """Execute TypeScript compiler"""
        try:
            cmd = ["npx", "tsc"]
            
            if watch:
                cmd.append("--watch")
            else:
                cmd.append("--noEmit")
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "TypeScript check passed"
            else:
                return f"TypeScript errors found:\n{result.stdout}"
                
        except Exception as e:
            return f"Error executing TypeScript: {str(e)}"


class ESLintTool(BaseTool):
    name: str = "eslint"
    description: str = "Run ESLint code linting"
    
    def _run(self, project_path: str, paths: Optional[List[str]] = None, fix: bool = False) -> str:
        """Execute ESLint"""
        try:
            cmd = ["npx", "eslint"]
            
            if fix:
                cmd.append("--fix")
            
            if paths:
                cmd.extend(paths)
            else:
                cmd.extend(["src/**/*.{js,ts,vue}"])
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "ESLint check passed"
            else:
                return f"ESLint issues found:\n{result.stdout}"
                
        except Exception as e:
            return f"Error executing ESLint: {str(e)}"


class VitestTool(BaseTool):
    name: str = "vitest"
    description: str = "Run Vitest tests"
    
    def _run(self, project_path: str, filter: Optional[str] = None, coverage: bool = False) -> str:
        """Execute Vitest"""
        try:
            cmd = ["npx", "vitest", "run"]
            
            if filter:
                cmd.extend(["--reporter=verbose", filter])
            
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
            return f"Error executing Vitest: {str(e)}"