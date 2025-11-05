"""
Logging configuration for SpendSense.

This module sets up structured logging using Python's logging module
with configuration for structured output (JSON format preparation for structlog).
"""

import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO",
    format_type: str = "text",
    log_file: Optional[str] = None
) -> None:
    """
    Configure application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format - "text" for human-readable, "json" for structured
        log_file: Optional file path to write logs to (in addition to console)

    Example:
        >>> configure_logging(level="DEBUG", format_type="text")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Define log format based on type
    if format_type == "json":
        # Structured format preparation (full structlog integration in future stories)
        log_format = '{"timestamp":"%(asctime)s", "level":"%(levelname)s", "module":"%(name)s", "message":"%(message)s"}'
    else:
        # Human-readable format
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Log configuration complete message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={level}, format={format_type}, "
        f"file={'Yes' if log_file else 'No'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
        >>> logger.info("Info message")
        >>> logger.warning("Warning message")
        >>> logger.error("Error message")
    """
    return logging.getLogger(name)


# Example usage demonstration
if __name__ == "__main__":
    # Configure logging
    configure_logging(level="DEBUG", format_type="text")

    # Get logger
    logger = get_logger(__name__)

    # Log examples at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Structured logging example
    print("\n--- Structured Logging Example ---\n")
    configure_logging(level="INFO", format_type="json")
    logger = get_logger("spendsense.example")
    logger.info("Application started successfully")
    logger.info("Processing user data")
    logger.warning("Approaching rate limit threshold")
