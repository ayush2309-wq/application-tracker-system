"""
logger.py – Audit/tracking logger for the Application Tracker System.

Writes structured log entries to both a rotating log file and stdout,
using only the Python standard library (logging module).
"""

import logging
import os
from datetime import datetime
from typing import Dict, List


_LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "tracker.log")

# Ensure the logs directory exists
os.makedirs(_LOG_DIR, exist_ok=True)


def _get_logger(name: str = "application_tracker") -> logging.Logger:
    """Return (and lazily configure) the module-level logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler – always append so history is preserved
        fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def log_run_start(jobs_count: int, applications_count: int) -> None:
    """Log the start of a matching run."""
    logger = _get_logger()
    logger.info(
        "=== Matching run started | jobs=%d | applications=%d ===",
        jobs_count,
        applications_count,
    )


def log_match_result(result: Dict) -> None:
    """Log a single match result.

    Args:
        result: A match-result dictionary produced by matcher.run_matching.
    """
    logger = _get_logger()
    status  = result.get("status", "Unknown")
    app_id  = result.get("application_id", "")
    name    = result.get("candidate_name", "")
    job_id  = result.get("job_id", "")
    title   = result.get("job_title", "")

    if result.get("qualified"):
        logger.info(
            "MOVE FORWARD | app=%s | candidate=%s | job=%s (%s)",
            app_id, name, job_id, title,
        )
    else:
        missing_tech = result.get("missing_technologies", [])
        missing_kw   = result.get("missing_keywords", [])
        exp_gap      = result.get("experience_gap", 0)
        logger.warning(
            "REGRET       | app=%s | candidate=%s | job=%s (%s) "
            "| missing_tech=%s | missing_kw=%s | exp_gap=%d",
            app_id, name, job_id, title,
            missing_tech, missing_kw, exp_gap,
        )


def log_all_results(results: List[Dict]) -> None:
    """Log every match result in the list.

    Args:
        results: List of match-result dicts from matcher.run_matching.
    """
    for result in results:
        log_match_result(result)


def log_run_summary(results: List[Dict]) -> None:
    """Log a summary of the matching run.

    Args:
        results: List of match-result dicts from matcher.run_matching.
    """
    logger   = _get_logger()
    total    = len(results)
    advanced = sum(1 for r in results if r.get("qualified"))
    regrets  = total - advanced

    logger.info(
        "=== Run summary | total=%d | move_forward=%d | regret=%d ===",
        total, advanced, regrets,
    )
