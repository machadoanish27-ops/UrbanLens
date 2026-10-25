"""Structured application logging with secret scrubbing."""

import logging
import re
import sys
from typing import Any

# Patterns to scrub from logs
SECRET_PATTERNS = [
    re.compile(r"mongodb(?:\+srv)?://([^:]+):([^@]+)@", re.IGNORECASE),
    re.compile(r"(password|secret|token|api_key|apikey|authorization)=([^\s&]+)", re.IGNORECASE),
]


class SecretScrubbingFormatter(logging.Formatter):
    """Log formatter that scrubs sensitive credentials from log messages."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        scrubbed = original
        for pattern in SECRET_PATTERNS:
            scrubbed = pattern.sub(r"mongodb+srv://\1:***@", scrubbed) if "mongodb" in pattern.pattern else pattern.sub(r"\1=***", scrubbed)
        return scrubbed


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger with sanitized stream handler."""
    logger = logging.getLogger("urbanlens")
    if logger.handlers:
        return

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = SecretScrubbingFormatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str = "urbanlens") -> logging.Logger:
    """Return a logger instance for the given namespace."""
    configure_logging()
    return logging.getLogger(f"urbanlens.{name}" if name != "urbanlens" else name)
