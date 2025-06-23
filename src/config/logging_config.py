"""
Logging configuration for CFTeam ecosystem
Provides structured logging with multiple handlers and formatters
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
from pythonjsonlogger import jsonlogger
from rich.logging import RichHandler
from rich.console import Console
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or text
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)

# Define log file paths
LOG_FILES = {
    "main": LOG_DIR / "cfteam.log",
    "agents": LOG_DIR / "agents.log",
    "crews": LOG_DIR / "crews.log",
    "tasks": LOG_DIR / "tasks.log",
    "errors": LOG_DIR / "errors.log",
    "database": LOG_DIR / "database.log",
    "redis": LOG_DIR / "redis.log",
    "api": LOG_DIR / "api.log",
}


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add module information
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add process and thread info
        log_record['process'] = record.process
        log_record['thread'] = record.thread
        
        # Add custom fields if present
        if hasattr(record, 'agent_id'):
            log_record['agent_id'] = record.agent_id
        if hasattr(record, 'task_id'):
            log_record['task_id'] = record.task_id
        if hasattr(record, 'session_id'):
            log_record['session_id'] = record.session_id
        if hasattr(record, 'crew_name'):
            log_record['crew_name'] = record.crew_name


class ContextFilter(logging.Filter):
    """Filter to add context information to log records"""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record):
        # Add context fields to record
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def get_file_handler(filename: Path, 
                    max_bytes: int = 10 * 1024 * 1024,  # 10MB
                    backup_count: int = 5) -> logging.handlers.RotatingFileHandler:
    """Create a rotating file handler"""
    handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    if LOG_FORMAT == "json":
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    return handler


def get_console_handler() -> logging.Handler:
    """Create a console handler"""
    if sys.stdout.isatty() and LOG_FORMAT != "json":
        # Use Rich handler for better console output
        console = Console(stderr=True)
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=DEBUG_MODE
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        # Use standard stream handler
        handler = logging.StreamHandler(sys.stdout)
        
        if LOG_FORMAT == "json":
            formatter = CustomJsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        handler.setFormatter(formatter)
    
    return handler


def setup_logging():
    """Setup logging configuration for the entire application"""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = get_console_handler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(console_handler)
    
    # Add main file handler
    main_file_handler = get_file_handler(LOG_FILES["main"])
    main_file_handler.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(main_file_handler)
    
    # Add error file handler (only ERROR and above)
    error_file_handler = get_file_handler(LOG_FILES["errors"])
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)
    
    # Configure specific loggers
    configure_module_loggers()
    
    # Set third-party library log levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        "CFTeam logging initialized",
        extra={
            "log_level": LOG_LEVEL,
            "log_format": LOG_FORMAT,
            "debug_mode": DEBUG_MODE
        }
    )


def configure_module_loggers():
    """Configure loggers for specific modules"""
    
    # Agent logger
    agent_logger = logging.getLogger("agent")
    agent_logger.setLevel(getattr(logging, LOG_LEVEL))
    agent_logger.addHandler(get_file_handler(LOG_FILES["agents"]))
    agent_logger.propagate = False
    
    # Crew logger
    crew_logger = logging.getLogger("crew")
    crew_logger.setLevel(getattr(logging, LOG_LEVEL))
    crew_logger.addHandler(get_file_handler(LOG_FILES["crews"]))
    crew_logger.propagate = False
    
    # Task logger
    task_logger = logging.getLogger("task")
    task_logger.setLevel(getattr(logging, LOG_LEVEL))
    task_logger.addHandler(get_file_handler(LOG_FILES["tasks"]))
    task_logger.propagate = False
    
    # Database logger
    db_logger = logging.getLogger("database")
    db_logger.setLevel(getattr(logging, LOG_LEVEL))
    db_logger.addHandler(get_file_handler(LOG_FILES["database"]))
    db_logger.propagate = False
    
    # Redis logger
    redis_logger = logging.getLogger("redis")
    redis_logger.setLevel(getattr(logging, LOG_LEVEL))
    redis_logger.addHandler(get_file_handler(LOG_FILES["redis"]))
    redis_logger.propagate = False
    
    # API logger
    api_logger = logging.getLogger("api")
    api_logger.setLevel(getattr(logging, LOG_LEVEL))
    api_logger.addHandler(get_file_handler(LOG_FILES["api"]))
    api_logger.propagate = False


def get_logger(name: str, 
               context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """Get a logger with optional context"""
    logger = logging.getLogger(name)
    
    if context:
        # Add context filter
        context_filter = ContextFilter(context)
        logger.addFilter(context_filter)
    
    return logger


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        self.logger.debug(message, extra=kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with extra fields"""
        if exception:
            self.logger.error(message, exc_info=exception, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        self.logger.critical(message, extra=kwargs)


def log_execution_time(func):
    """Decorator to log function execution time"""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = get_logger(func.__module__)
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "success"
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                f"Function {func.__name__} failed",
                exc_info=e,
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "failed",
                    "error": str(e)
                }
            )
            
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = get_logger(func.__module__)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "success"
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                f"Function {func.__name__} failed",
                exc_info=e,
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "failed",
                    "error": str(e)
                }
            )
            
            raise
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Initialize logging when module is imported
setup_logging()