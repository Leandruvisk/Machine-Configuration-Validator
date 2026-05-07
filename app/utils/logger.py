import logging
import os
from pathlib import Path

def get_logger(name: str = "machine_validator", level: str = None):
    """Get configured logger instance"""
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, level, logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler if not already added
    if not logger.handlers:
        logger.addHandler(handler)

    return logger