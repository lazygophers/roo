"""
This module provides a configurable logger for the application.
"""

import logging
import sys


def setup_logger(debug: bool) -> None:
    """
    Set up the root logger for the application.

    This function configures the root logger. When debug mode is enabled,
    it sets the logging level to DEBUG. When disabled, it effectively silences
    all logging by setting the level to a value higher than CRITICAL.
    All log messages are directed to stderr to avoid interfering with stdout,
    which may be used for Model-Copilot-Protocol (MCP) communication.

    Args:
        debug (bool): A flag to enable or disable debug-level logging.
                      If True, the log level is set to logging.DEBUG.
                      If False, logging is disabled by setting the level
                      to CRITICAL + 1.
    """
    logger = logging.getLogger()

    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    if debug:
        level: int | str = logging.DEBUG
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        # A level higher than any standard level to disable logging
        level = logging.CRITICAL + 1
        log_format = "%(message)s"  # Basic format when not in debug

    logger.setLevel(level)

    # Direct all logs to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Set the formatter
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    logging.debug("Logger has been set up.")
