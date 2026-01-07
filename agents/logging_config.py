"""
LOGGING_CONFIG.PY
=================

Central logging configuration for Showcase application.
"""

import logging
from logging.config import dictConfig
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)


def setup_logging(
    level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True
) -> None:
    """
    Configure logging for Showcase.
    
    Args:
        level: Base logging level (DEBUG/INFO/WARNING/ERROR).
        log_to_console: Enable console output.
        log_to_file: Enable rotating file logs.
    
    Example:
        setup_logging(level="DEBUG", log_to_console=True, log_to_file=True)
    """
    
    # Build root handlers dynamically
    root_handlers = []
    if log_to_console:
        root_handlers.append("console")
    if log_to_file:
        root_handlers.extend(["file", "error_file"])
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": str(LOG_DIR / "showcase.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": level,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": str(LOG_DIR / "showcase_error.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": "ERROR",
            },
        },
        "root": {
            "handlers": root_handlers,
            "level": level,
        },
        "loggers": {
            "uvicorn": {"level": level},
            "uvicorn.error": {"level": level},
            "uvicorn.access": {"level": "INFO"},
        },
    }
    
    dictConfig(config)
    
    # Log startup
    logger = logging.getLogger("showcase")
    logger.info(
        f"Logging initialized | level={level} | console={log_to_console} | file={log_to_file}"
    )


# Usage example
if __name__ == "__main__":
    # Initialize logging
    setup_logging(level="DEBUG", log_to_console=True, log_to_file=True)
    
    # Test loggers
    root_logger = logging.getLogger()
    app_logger = logging.getLogger("showcase")
    uvicorn_logger = logging.getLogger("uvicorn")
    
    root_logger.info("Root logger test")
    app_logger.info("App logger test")
    uvicorn_logger.debug("Uvicorn logger debug test")
    app_logger.error("Error logger test")
    
    print(f"\n✓ Logs created in: {LOG_DIR}")
    print(f"  - showcase.log (all logs)")
    print(f"  - showcase_error.log (errors only)")