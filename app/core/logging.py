"""
Central Logging Configuration for Showcase AI.

This module provides a centralized, configurable logging setup that can be used 
across the entire application and agent system.

Usage:
    from app.core.logging import setup_logging, get_logger
    
    # At application startup
    setup_logging(level="DEBUG", log_to_file=True)
    
    # In any module
    logger = get_logger(__name__)
    logger.info("Processing started", extra={"job_id": "123"})
"""

import logging
import sys
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache


# Default log directory
LOG_DIR = Path("logs")


class ContextFilter(logging.Filter):
    """
    Filter that adds context information to log records.
    
    This allows adding request IDs, job IDs, or other context
    to all log messages within a request/task.
    """
    
    def __init__(self, name: str = "", context: Optional[Dict[str, Any]] = None):
        super().__init__(name)
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class ShowcaseFormatter(logging.Formatter):
    """
    Custom formatter with colored output for console logging.
    
    Adds colors for different log levels when outputting to a terminal.
    """
    
    # ANSI color codes
    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def __init__(self, fmt: str, datefmt: str = None, use_colors: bool = True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            color = self.COLORS.get(record.levelno, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True,
    log_dir: Optional[Path] = None,
    json_format: bool = False
) -> None:
    """
    Configure logging for the Showcase application.
    
    Args:
        level: Base logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_to_console: Enable console output
        log_to_file: Enable rotating file logs
        log_dir: Custom log directory (defaults to ./logs)
        json_format: Use JSON format for structured logging
    
    Example:
        setup_logging(level="DEBUG", log_to_console=True, log_to_file=True)
    """
    # Create log directory
    log_path = log_dir or LOG_DIR
    if log_to_file:
        log_path.mkdir(exist_ok=True, parents=True)
    
    # Format strings
    console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Build handlers list
    handlers = {}
    root_handlers = []
    
    if log_to_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": level,
            "stream": "ext://sys.stdout",
        }
        root_handlers.append("console")
    
    if log_to_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": str(log_path / "showcase.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
            "level": level,
        }
        handlers["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": str(log_path / "showcase_error.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
            "level": "ERROR",
        }
        root_handlers.extend(["file", "error_file"])
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": ShowcaseFormatter,
                "fmt": console_format,
                "datefmt": date_format,
                "use_colors": True,
            },
            "detailed": {
                "format": file_format,
                "datefmt": date_format,
            },
        },
        "handlers": handlers,
        "root": {
            "handlers": root_handlers,
            "level": level,
        },
        "loggers": {
            # Application loggers
            "app": {"level": level},
            "agents": {"level": level},
            "showcase": {"level": level},
            
            # Framework loggers
            "uvicorn": {"level": level},
            "uvicorn.error": {"level": level},
            "uvicorn.access": {"level": "INFO"},
            "celery": {"level": level},
            
            # Reduce noise from third-party libraries
            "httpx": {"level": "WARNING"},
            "httpcore": {"level": "WARNING"},
            "google": {"level": "WARNING"},
        },
    }
    
    dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger("showcase")
    logger.info(
        f"Logging initialized | level={level} | console={log_to_console} | file={log_to_file}"
    )


@lru_cache(maxsize=128)
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.
    
    This function is cached for performance when called multiple times
    with the same name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context
) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Logging level (e.g., logging.INFO)
        message: Log message
        **context: Additional context fields to include
    
    Example:
        log_with_context(logger, logging.INFO, "Job started", job_id="123", user="alice")
    """
    extra = {"context": context} if context else {}
    logger.log(level, message, extra=extra)


# Convenience function for quick setup
def quick_setup(debug: bool = False) -> None:
    """
    Quick logging setup with sensible defaults.
    
    Args:
        debug: Enable debug logging
    """
    level = "DEBUG" if debug else "INFO"
    setup_logging(level=level, log_to_console=True, log_to_file=False)


# Module-level test
if __name__ == "__main__":
    setup_logging(level="DEBUG", log_to_console=True, log_to_file=True)
    
    logger = get_logger("showcase.test")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    print(f"\n✓ Logs created in: {LOG_DIR}")
