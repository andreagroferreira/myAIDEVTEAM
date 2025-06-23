"""
Git tools for CrewAI agents
"""

from typing import List, Dict, Any, Optional
import subprocess
import os
from crewai_tools import BaseTool


class GitStatusTool(BaseTool):
    name: str = "git_status"
    description: str = "Check git status of a project"
    
    def _run(self, project_path: str) -> str:
        """Execute git status command"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout if result.stdout else "Working directory clean"
            
        except Exception as e:
            return f"Error executing git status: {str(e)}"


class GitCommitTool(BaseTool):
    name: str = "git_commit"
    description: str = "Commit changes with a message"
    
    def _run(self, project_path: str, message: str, files: Optional[List[str]] = None) -> str:
        """Execute git commit"""
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(["git", "add", file], cwd=project_path)
            else:
                subprocess.run(["git", "add", "-A"], cwd=project_path)
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Successfully committed: {message}"
            else:
                return f"Commit failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing git commit: {str(e)}"


class GitBranchTool(BaseTool):
    name: str = "git_branch"
    description: str = "Create or switch git branches"
    
    def _run(self, project_path: str, branch_name: str, create: bool = False) -> str:
        """Execute git branch operations"""
        try:
            if create:
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return f"Switched to branch '{branch_name}'"
            else:
                return f"Branch operation failed: {result.stderr}"
                
        except Exception as e:
            return f"Error with git branch: {str(e)}"


class GitDiffTool(BaseTool):
    name: str = "git_diff"
    description: str = "Show git diff for files"
    
    def _run(self, project_path: str, files: Optional[List[str]] = None) -> str:
        """Execute git diff"""
        try:
            cmd = ["git", "diff"]
            if files:
                cmd.extend(files)
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "No differences found"
            else:
                return f"Diff failed: {result.stderr}"
                
        except Exception as e:
            return f"Error executing git diff: {str(e)}"