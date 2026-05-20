import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging() -> logging.Logger:
    """Defines the log format, like timestamp, level, logger name and message."""
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False

    return logger
