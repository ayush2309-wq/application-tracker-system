"""
__init__.py – Exposes the public API of the src package.
"""

from .data_loader import load_jobs, load_applications
from .matcher import run_matching, match_application
from .notifier import send_notifications, compose_notification
from .logger import log_run_start, log_all_results, log_run_summary

__all__ = [
    "load_jobs",
    "load_applications",
    "run_matching",
    "match_application",
    "send_notifications",
    "compose_notification",
    "log_run_start",
    "log_all_results",
    "log_run_summary",
]
