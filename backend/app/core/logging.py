"""Structured logging setup (stdlib logging, single-line format)."""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once. Swap for JSON structured logs later if needed."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
