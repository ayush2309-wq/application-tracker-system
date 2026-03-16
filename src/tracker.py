"""
Core tracker for the Application Tracker System.

Orchestrates loading data, running matches, sending notifications, and
persisting results.
"""

import json
import os
from typing import Dict, List, Optional

from .logger import get_logger, log_event
from .matcher import match_application, rank_applications
from .models import Application, JobRequirement, MatchResult
from .notifier import notify_all

logger = get_logger("tracker")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RESULTS_PATH = os.path.join(DATA_DIR, "results.json")


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_job_requirements(path: Optional[str] = None) -> List[JobRequirement]:
    """Load job requirements from a JSON file."""
    path = path or os.path.join(DATA_DIR, "job_requirements.json")
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    jobs = [JobRequirement(**item) for item in raw]
    logger.info("Loaded %d job requirement(s) from %s", len(jobs), path)
    return jobs


def load_applications(path: Optional[str] = None) -> List[Application]:
    """Load applications from a JSON file."""
    path = path or os.path.join(DATA_DIR, "applications.json")
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    apps = [Application(**item) for item in raw]
    logger.info("Loaded %d application(s) from %s", len(apps), path)
    return apps


# ---------------------------------------------------------------------------
# Result persistence
# ---------------------------------------------------------------------------

def save_results(results: List[MatchResult], path: Optional[str] = None) -> None:
    """Persist match results as JSON."""
    path = path or RESULTS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serializable = [r.__dict__ for r in results]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, indent=2)
    logger.info("Saved %d result(s) to %s", len(results), path)


# ---------------------------------------------------------------------------
# High-level workflows
# ---------------------------------------------------------------------------

def process_applications(
    applications: List[Application],
    jobs: List[JobRequirement],
    emails: Optional[Dict[str, str]] = None,
    notify: bool = True,
) -> List[MatchResult]:
    """
    Match every application against every job, determine status, and
    optionally send notifications.

    Returns all MatchResult objects sorted by score descending.
    """
    all_results: List[MatchResult] = []

    for app in applications:
        logger.info("Processing application %s (%s)", app.application_id, app.applicant_name)
        results = match_application(app, jobs)
        all_results.extend(results)
        log_event(
            "application_processed",
            {
                "application_id": app.application_id,
                "applicant_name": app.applicant_name,
                "num_jobs_evaluated": len(jobs),
                "best_score": results[0].match_score if results else 0,
            },
        )

    all_results.sort(key=lambda r: r.match_score, reverse=True)

    if notify:
        notify_all(all_results, emails=emails)

    save_results(all_results)
    return all_results


def rank_for_job(job_id: str, applications: List[Application], jobs: List[JobRequirement]) -> List[MatchResult]:
    """Return ranked applicants for a specific job."""
    job_map = {j.job_id: j for j in jobs}
    if job_id not in job_map:
        raise ValueError(f"Job ID '{job_id}' not found.")
    job = job_map[job_id]
    ranked = rank_applications(applications, job)
    logger.info(
        "Ranked %d applicant(s) for job %s (%s)", len(ranked), job_id, job.title
    )
    return ranked
