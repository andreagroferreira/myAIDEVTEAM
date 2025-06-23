"""
Git Coordinator service for CFTeam ecosystem
Manages git operations across multiple projects
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess

from src.config import get_logger, RedisCache, RedisPubSub, CHANNELS


class GitCoordinator:
    """Coordinates git operations across projects"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = RedisCache()
        self.pubsub = RedisPubSub()
        
    async def create_checkpoint(
        self, 
        projects: List[str], 
        checkpoint_name: str,
        message: str
    ) -> Dict[str, Any]:
        """Create git checkpoint across multiple projects"""
        results = {}
        
        for project_path in projects:
            try:
                # Create branch
                branch_name = f"checkpoint/{checkpoint_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                # Git commands
                commands = [
                    f"cd {project_path} && git checkout -b {branch_name}",
                    f"cd {project_path} && git add -A",
                    f"cd {project_path} && git commit -m '{message}' || true"
                ]
                
                for cmd in commands:
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                
                results[project_path] = {
                    'success': True,
                    'branch': branch_name
                }
                
                self.logger.info(f"Created checkpoint {branch_name} for {project_path}")
                
            except Exception as e:
                results[project_path] = {
                    'success': False,
                    'error': str(e)
                }
                self.logger.error(f"Failed to create checkpoint for {project_path}: {e}")
        
        # Publish checkpoint event
        await self.pubsub.publish(
            CHANNELS['git_updates'],
            {
                'action': 'checkpoint_created',
                'checkpoint_name': checkpoint_name,
                'results': results
            }
        )
        
        return results
    
    async def get_status(self, project_path: str) -> Dict[str, Any]:
        """Get git status for a project"""
        try:
            process = await asyncio.create_subprocess_shell(
                f"cd {project_path} && git status --porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {'error': stderr.decode()}
            
            # Parse status
            lines = stdout.decode().strip().split('\n')
            files = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': []
            }
            
            for line in lines:
                if not line:
                    continue
                    
                status = line[:2]
                filename = line[3:]
                
                if 'M' in status:
                    files['modified'].append(filename)
                elif 'A' in status:
                    files['added'].append(filename)
                elif 'D' in status:
                    files['deleted'].append(filename)
                elif '??' in status:
                    files['untracked'].append(filename)
            
            # Get current branch
            branch_process = await asyncio.create_subprocess_shell(
                f"cd {project_path} && git rev-parse --abbrev-ref HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            branch_stdout, _ = await branch_process.communicate()
            current_branch = branch_stdout.decode().strip()
            
            return {
                'branch': current_branch,
                'files': files,
                'clean': len(files['modified']) == 0 and len(files['added']) == 0 and len(files['deleted']) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get git status for {project_path}: {e}")
            return {'error': str(e)}
    
    async def commit_changes(
        self,
        project_path: str,
        message: str,
        files: Optional[List[str]] = None
    ) -> bool:
        """Commit changes in a project"""
        try:
            # Add files
            if files:
                for file in files:
                    cmd = f"cd {project_path} && git add {file}"
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await process.communicate()
            else:
                # Add all files
                cmd = f"cd {project_path} && git add -A"
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            
            # Commit
            commit_cmd = f"cd {project_path} && git commit -m '{message}'"
            process = await asyncio.create_subprocess_shell(
                commit_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"Committed changes in {project_path}")
                
                # Publish commit event
                await self.pubsub.publish(
                    CHANNELS['git_updates'],
                    {
                        'action': 'committed',
                        'project': project_path,
                        'message': message
                    }
                )
                
                return True
            else:
                self.logger.error(f"Failed to commit in {project_path}: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to commit changes in {project_path}: {e}")
            return False
    
    async def sync_branches(
        self,
        project_path: str,
        source_branch: str,
        target_branch: str
    ) -> bool:
        """Sync branches in a project"""
        try:
            commands = [
                f"cd {project_path} && git checkout {target_branch}",
                f"cd {project_path} && git merge {source_branch} --no-ff -m 'Merge {source_branch} into {target_branch}'"
            ]
            
            for cmd in commands:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    self.logger.error(f"Failed to sync branches: {stderr.decode()}")
                    return False
            
            self.logger.info(f"Synced {source_branch} into {target_branch} for {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync branches in {project_path}: {e}")
            return False