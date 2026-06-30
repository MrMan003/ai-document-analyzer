"""
Structured logging configuration.
"""
import logging
import sys
from typing import Dict, Any
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = self.formatTime(record, self.datefmt)
        if not log_record.get("level"):
            log_record["level"] = record.levelname
        if not log_record.get("logger"):
            log_record["logger"] = record.name


def setup_logging():
    """Configure logging based on environment."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.LOG_FORMAT == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)