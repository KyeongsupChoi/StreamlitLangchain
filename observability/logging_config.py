"""
Logging configuration for LangChainExpo.

Project role:
  Provide a single place to configure file-based logging (no print-based ops logs).
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(*, log_file_path: str = "logs/app.log") -> None:
    """
    Configure root logging with a rotating file handler.

    Params:
      log_file_path: Path to the log file (created if missing).
    """

    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Avoid duplicate handlers in Streamlit's re-run model.
        return

    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
