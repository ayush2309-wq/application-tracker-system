"""
File-based logger for the Application Tracker System.

All events are appended to a rotating daily log file under the /logs directory.
"""

import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "tracker.log")
MAX_BYTES = 1_000_000  # 1 MB per file
BACKUP_COUNT = 5


def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str = "tracker") -> logging.Logger:
    """Return a configured logger that writes to both console and a rotating file."""
    _ensure_log_dir()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_event(event_type: str, payload: dict) -> None:
    """Append a structured JSON event entry to the event log."""
    _ensure_log_dir()
    event_log_path = os.path.join(LOG_DIR, "events.jsonl")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **payload,
    }
    with open(event_log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
