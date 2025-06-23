"""
Notification Service for CFTeam ecosystem
Handles notifications via webhooks, Slack, Discord, and internal channels
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from src.config import get_logger, RedisCache, RedisPubSub, CHANNELS


class NotificationService:
    """Manages notifications across different channels"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cache = RedisCache()
        self.pubsub = RedisPubSub()
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def notify(
        self,
        message: str,
        level: str = "info",
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Send notification to specified channels"""
        results = {}
        
        notification = {
            'message': message,
            'level': level,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        # Default to internal channel if none specified
        if not channels:
            channels = ['internal']
        
        for channel in channels:
            try:
                if channel == 'internal':
                    await self._notify_internal(notification)
                    results['internal'] = True
                elif channel == 'slack':
                    results['slack'] = await self._notify_slack(notification)
                elif channel == 'discord':
                    results['discord'] = await self._notify_discord(notification)
                elif channel == 'webhook':
                    results['webhook'] = await self._notify_webhook(notification)
                    
            except Exception as e:
                self.logger.error(f"Failed to notify {channel}: {e}")
                results[channel] = False
        
        return results
    
    async def _notify_internal(self, notification: Dict[str, Any]):
        """Send notification via internal Redis pub/sub"""
        await self.pubsub.publish(
            CHANNELS['notifications'],
            notification
        )
    
    async def _notify_slack(self, notification: Dict[str, Any]) -> bool:
        """Send notification to Slack"""
        import os
        webhook_url = os.getenv('SLACK_WEBHOOK')
        
        if not webhook_url:
            self.logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            # Format message for Slack
            color_map = {
                'error': '#FF0000',
                'warning': '#FFA500',
                'success': '#00FF00',
                'info': '#0000FF'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(notification['level'], '#808080'),
                    'title': f"CFTeam {notification['level'].upper()}",
                    'text': notification['message'],
                    'timestamp': int(datetime.fromisoformat(notification['timestamp']).timestamp()),
                    'fields': [
                        {'title': k, 'value': str(v), 'short': True}
                        for k, v in notification['metadata'].items()
                    ]
                }]
            }
            
            response = await self.client.post(webhook_url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def _notify_discord(self, notification: Dict[str, Any]) -> bool:
        """Send notification to Discord"""
        import os
        webhook_url = os.getenv('DISCORD_WEBHOOK')
        
        if not webhook_url:
            self.logger.warning("Discord webhook URL not configured")
            return False
        
        try:
            # Format message for Discord
            color_map = {
                'error': 0xFF0000,
                'warning': 0xFFA500,
                'success': 0x00FF00,
                'info': 0x0000FF
            }
            
            payload = {
                'embeds': [{
                    'title': f"CFTeam {notification['level'].upper()}",
                    'description': notification['message'],
                    'color': color_map.get(notification['level'], 0x808080),
                    'timestamp': notification['timestamp'],
                    'fields': [
                        {'name': k, 'value': str(v), 'inline': True}
                        for k, v in notification['metadata'].items()
                    ]
                }]
            }
            
            response = await self.client.post(webhook_url, json=payload)
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    async def _notify_webhook(self, notification: Dict[str, Any]) -> bool:
        """Send notification to generic webhook"""
        import os
        webhook_url = os.getenv('WEBHOOK_URL')
        
        if not webhook_url:
            self.logger.warning("Webhook URL not configured")
            return False
        
        try:
            response = await self.client.post(webhook_url, json=notification)
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    async def notify_session_event(
        self,
        session_id: str,
        event: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Notify about session events"""
        message = f"Session {session_id}: {event}"
        
        metadata = {
            'session_id': session_id,
            'event': event,
            **(details or {})
        }
        
        level_map = {
            'created': 'info',
            'started': 'info',
            'completed': 'success',
            'failed': 'error',
            'paused': 'warning'
        }
        
        await self.notify(
            message=message,
            level=level_map.get(event, 'info'),
            metadata=metadata
        )
    
    async def notify_task_event(
        self,
        task_id: str,
        event: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Notify about task events"""
        message = f"Task {task_id}: {event}"
        
        metadata = {
            'task_id': task_id,
            'event': event,
            **(details or {})
        }
        
        level_map = {
            'created': 'info',
            'assigned': 'info',
            'started': 'info',
            'completed': 'success',
            'failed': 'error',
            'blocked': 'warning'
        }
        
        await self.notify(
            message=message,
            level=level_map.get(event, 'info'),
            metadata=metadata
        )
    
    async def notify_error(
        self,
        component: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Notify about errors"""
        message = f"Error in {component}: {error}"
        
        metadata = {
            'component': component,
            'error': error,
            **(details or {})
        }
        
        await self.notify(
            message=message,
            level='error',
            channels=['internal', 'slack', 'discord'],
            metadata=metadata
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()