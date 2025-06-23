"""
Redis configuration for CFTeam ecosystem
Handles Redis connections for real-time communication and caching
"""

import os
import json
from typing import Optional, Any, Dict, List
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from dotenv import load_dotenv
import logging
from datetime import timedelta

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Redis configuration from environment
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True,
    'encoding': 'utf-8',
    'health_check_interval': 30,
}

# Global Redis client and connection pool
redis_client: Optional[redis.Redis] = None
connection_pool: Optional[ConnectionPool] = None

# Channel names for pub/sub
CHANNELS = {
    'agent_communication': 'cfteam:agents:comm',
    'task_updates': 'cfteam:tasks:updates',
    'crew_coordination': 'cfteam:crews:coord',
    'system_events': 'cfteam:system:events',
    'error_reports': 'cfteam:errors:reports',
}

# Cache key prefixes
CACHE_PREFIXES = {
    'session': 'cfteam:session:',
    'task': 'cfteam:task:',
    'agent': 'cfteam:agent:',
    'crew': 'cfteam:crew:',
    'result': 'cfteam:result:',
    'lock': 'cfteam:lock:',
}

# Default TTL values (in seconds)
DEFAULT_TTL = {
    'session': 3600,  # 1 hour
    'task': 86400,    # 24 hours
    'result': 604800, # 7 days
    'lock': 300,      # 5 minutes
}


async def init_redis():
    """Initialize Redis connection"""
    global redis_client, connection_pool
    
    try:
        # Create connection pool
        connection_pool = ConnectionPool(
            **REDIS_CONFIG,
            max_connections=50,
        )
        
        # Create Redis client
        redis_client = redis.Redis(connection_pool=connection_pool)
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection initialized successfully")
        
        # Set up key expiration notifications
        await redis_client.config_set('notify-keyspace-events', 'Ex')
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        await init_redis()
    return redis_client


async def close_redis():
    """Close Redis connections"""
    global redis_client, connection_pool
    
    if redis_client:
        await redis_client.close()
        redis_client = None
    
    if connection_pool:
        await connection_pool.disconnect()
        connection_pool = None
    
    logger.info("Redis connections closed")


class RedisCache:
    """High-level cache operations"""
    
    def __init__(self, prefix: str = ''):
        self.prefix = prefix
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        client = await get_redis_client()
        value = await client.get(f"{self.prefix}{key}")
        
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        client = await get_redis_client()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        full_key = f"{self.prefix}{key}"
        
        if ttl:
            await client.setex(full_key, ttl, value)
        else:
            await client.set(full_key, value)
    
    async def delete(self, key: str):
        """Delete value from cache"""
        client = await get_redis_client()
        await client.delete(f"{self.prefix}{key}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        client = await get_redis_client()
        return await client.exists(f"{self.prefix}{key}") > 0
    
    async def expire(self, key: str, ttl: int):
        """Set expiration on key"""
        client = await get_redis_client()
        await client.expire(f"{self.prefix}{key}", ttl)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values"""
        client = await get_redis_client()
        full_keys = [f"{self.prefix}{key}" for key in keys]
        values = await client.mget(full_keys)
        
        result = {}
        for key, value in zip(keys, values):
            if value:
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
        
        return result
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values"""
        client = await get_redis_client()
        
        # Prepare values
        prepared = {}
        for key, value in mapping.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            prepared[f"{self.prefix}{key}"] = value
        
        # Set all values
        await client.mset(prepared)
        
        # Set TTL if provided
        if ttl:
            pipeline = client.pipeline()
            for key in prepared.keys():
                pipeline.expire(key, ttl)
            await pipeline.execute()


class RedisPubSub:
    """Pub/Sub operations for agent communication"""
    
    def __init__(self):
        self.pubsub = None
        self.subscriptions = set()
    
    async def subscribe(self, channels: List[str]):
        """Subscribe to channels"""
        client = await get_redis_client()
        
        if not self.pubsub:
            self.pubsub = client.pubsub()
        
        await self.pubsub.subscribe(*channels)
        self.subscriptions.update(channels)
        logger.info(f"Subscribed to channels: {channels}")
    
    async def unsubscribe(self, channels: Optional[List[str]] = None):
        """Unsubscribe from channels"""
        if self.pubsub:
            if channels:
                await self.pubsub.unsubscribe(*channels)
                self.subscriptions.difference_update(channels)
            else:
                await self.pubsub.unsubscribe()
                self.subscriptions.clear()
    
    async def publish(self, channel: str, message: Any):
        """Publish message to channel"""
        client = await get_redis_client()
        
        if isinstance(message, dict):
            message = json.dumps(message)
        
        await client.publish(channel, message)
    
    async def listen(self):
        """Listen for messages"""
        if not self.pubsub:
            raise RuntimeError("Not subscribed to any channels")
        
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = message['data']
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass
                
                yield {
                    'channel': message['channel'],
                    'data': data
                }
    
    async def close(self):
        """Close pub/sub connection"""
        if self.pubsub:
            await self.pubsub.close()
            self.pubsub = None
            self.subscriptions.clear()


class RedisLock:
    """Distributed locking using Redis"""
    
    def __init__(self, key: str, timeout: int = 300):
        self.key = f"{CACHE_PREFIXES['lock']}{key}"
        self.timeout = timeout
        self.identifier = None
    
    async def acquire(self) -> bool:
        """Acquire lock"""
        import uuid
        client = await get_redis_client()
        
        self.identifier = str(uuid.uuid4())
        return await client.set(
            self.key, 
            self.identifier, 
            nx=True, 
            ex=self.timeout
        )
    
    async def release(self) -> bool:
        """Release lock"""
        if not self.identifier:
            return False
        
        client = await get_redis_client()
        
        # Use Lua script to ensure atomic release
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await client.eval(lua_script, 1, self.key, self.identifier)
        return result == 1
    
    async def extend(self, additional_time: int) -> bool:
        """Extend lock timeout"""
        if not self.identifier:
            return False
        
        client = await get_redis_client()
        
        # Check if we still own the lock
        current = await client.get(self.key)
        if current == self.identifier:
            return await client.expire(self.key, self.timeout + additional_time)
        
        return False
    
    async def __aenter__(self):
        """Context manager entry"""
        if not await self.acquire():
            raise RuntimeError(f"Could not acquire lock for {self.key}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.release()


# Utility functions
async def health_check() -> dict:
    """Check Redis health"""
    try:
        client = await get_redis_client()
        
        # Ping Redis
        await client.ping()
        
        # Get info
        info = await client.info()
        
        return {
            "status": "healthy",
            "connected_clients": info.get('connected_clients', 0),
            "used_memory": info.get('used_memory_human', 'N/A'),
            "uptime_days": info.get('uptime_in_days', 0),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def flush_cache(pattern: str = None):
    """Flush cache entries matching pattern"""
    client = await get_redis_client()
    
    if pattern:
        # Find all keys matching pattern
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        
        # Delete keys in batches
        if keys:
            for i in range(0, len(keys), 1000):
                batch = keys[i:i+1000]
                await client.delete(*batch)
            
            logger.info(f"Flushed {len(keys)} keys matching pattern: {pattern}")
    else:
        # Flush entire database
        await client.flushdb()
        logger.warning("Flushed entire Redis database")