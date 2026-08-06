"""
logger_utils.py - Provides a standard logger configuration.
"""

import logging
import os
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with console and file handlers.
    
    Args:
        name: Name of the logger (typically __name__).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, assume it's configured to avoid duplicate logs.
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "target")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "automation.log")
    
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
