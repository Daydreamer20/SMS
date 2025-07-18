"""
Production logging configuration.
"""

import logging
import logging.config
import sys
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
        },
    }
    
    # In production, use JSON formatter for better log parsing
    if settings.ENVIRONMENT == "production":
        for handler in logging_config["handlers"].values():
            if handler.get("formatter") in ["default", "detailed"]:
                handler["formatter"] = "json"
    
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Security audit logger
security_logger = logging.getLogger("security")
security_handler = logging.handlers.RotatingFileHandler(
    "logs/security.log", maxBytes=10485760, backupCount=10
)
security_formatter = logging.Formatter(
    "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
)
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)


def log_security_event(event_type: str, details: Dict[str, Any], request_info: Dict[str, Any] = None):
    """Log security-related events."""
    log_data = {
        "event_type": event_type,
        "details": details,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="security", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
    }
    
    if request_info:
        log_data["request"] = request_info
    
    security_logger.info(f"Security Event: {log_data}")


# Performance logger
performance_logger = logging.getLogger("performance")
performance_handler = logging.handlers.RotatingFileHandler(
    "logs/performance.log", maxBytes=10485760, backupCount=5
)
performance_formatter = logging.Formatter(
    "%(asctime)s - PERFORMANCE - %(message)s"
)
performance_handler.setFormatter(performance_formatter)
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)