"""Centralized logging setup for DecisionOS backend."""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures structured logging for the application."""
    logger = logging.getLogger("decisionos")
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
