"""Centralized logging setup for PawPal+.

Writes structured-ish lines to logs/pawpal.log and stderr. Imported once at app
or CLI startup so every module that calls `logging.getLogger("pawpal.*")`
inherits the same config.
"""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging(level: str = "INFO") -> None:
    log_dir = os.environ.get("PAWPAL_LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    root = logging.getLogger("pawpal")
    if root.handlers:
        return  # already configured

    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "pawpal.log"),
        maxBytes=512_000,
        backupCount=2,
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    root.addHandler(stream)
