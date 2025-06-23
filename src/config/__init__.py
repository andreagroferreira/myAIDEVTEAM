"""
Configuration module for CFTeam ecosystem
"""

from src.config.database import (
    init_database,
    get_db_session,
    create_tables,
    close_database,
    db_pool,
    health_check as db_health_check
)

from src.config.redis_config import (
    init_redis,
    get_redis_client,
    close_redis,
    RedisCache,
    RedisPubSub,
    RedisLock,
    health_check as redis_health_check,
    CHANNELS,
    CACHE_PREFIXES
)

from src.config.logging_config import (
    setup_logging,
    get_logger,
    LoggerMixin,
    log_execution_time
)

from src.config.yaml_loader import (
    YAMLConfigLoader,
    config_loader,
    get_agent_config,
    get_crew_config,
    get_project_config,
    list_available_agents,
    list_available_crews,
    list_available_projects
)

__all__ = [
    # Database
    "init_database",
    "get_db_session",
    "create_tables",
    "close_database",
    "db_pool",
    "db_health_check",
    
    # Redis
    "init_redis",
    "get_redis_client", 
    "close_redis",
    "RedisCache",
    "RedisPubSub",
    "RedisLock",
    "redis_health_check",
    "CHANNELS",
    "CACHE_PREFIXES",
    
    # Logging
    "setup_logging",
    "get_logger",
    "LoggerMixin",
    "log_execution_time",
    
    # YAML Loader
    "YAMLConfigLoader",
    "config_loader",
    "get_agent_config",
    "get_crew_config",
    "get_project_config",
    "list_available_agents",
    "list_available_crews",
    "list_available_projects",
]