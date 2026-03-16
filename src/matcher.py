"""
matcher.py – Compares candidate applications against job requirements.

Matching criteria
-----------------
1. Technologies  – Candidate must list ALL required technologies (case-insensitive).
2. Keywords      – Candidate must include ALL required keywords (case-insensitive).
3. Experience    – Candidate's experience_years must meet or exceed min_experience_years.

A candidate is considered *qualified* only when all three criteria are satisfied.
"""

from typing import Dict, List


def _normalize(items: List[str]) -> List[str]:
    """Return a list of lower-cased, stripped strings."""
    return [s.strip().lower() for s in items]


def match_application(application: Dict, job: Dict) -> Dict:
    """Evaluate a single application against a job's requirements.

    Args:
        application: Candidate application dictionary.
        job:         Job requirements dictionary.

    Returns:
        A result dictionary with keys:
            - application_id (str)
            - candidate_name (str)
            - email (str)
            - job_id (str)
            - job_title (str)
            - qualified (bool)
            - missing_technologies (list[str])
            - missing_keywords (list[str])
            - experience_gap (int)  – negative means surplus, positive means deficit
            - status (str)  – "Move Forward" | "Regret"
    """
    required_tech = _normalize(job.get("required_technologies", []))
    required_kw   = _normalize(job.get("required_keywords", []))
    min_exp       = job.get("min_experience_years", 0)

    candidate_tech = _normalize(application.get("technologies", []))
    candidate_kw   = _normalize(application.get("keywords", []))
    candidate_exp  = application.get("experience_years", 0)

    missing_tech = [t for t in required_tech if t not in candidate_tech]
    missing_kw   = [k for k in required_kw   if k not in candidate_kw]
    exp_gap      = min_exp - candidate_exp  # positive → deficit

    qualified = not missing_tech and not missing_kw and exp_gap <= 0

    return {
        "application_id":       application.get("application_id", ""),
        "candidate_name":       application.get("candidate_name", ""),
        "email":                application.get("email", ""),
        "job_id":               job.get("job_id", ""),
        "job_title":            job.get("title", ""),
        "qualified":            qualified,
        "missing_technologies": missing_tech,
        "missing_keywords":     missing_kw,
        "experience_gap":       exp_gap,
        "status":               "Move Forward" if qualified else "Regret",
    }


def run_matching(applications: List[Dict], jobs: List[Dict]) -> List[Dict]:
    """Match every application to its corresponding job.

    Applications whose job_id does not exist in the jobs list are skipped
    (a warning is embedded in the result).

    Args:
        applications: List of candidate application dicts.
        jobs:         List of job requirement dicts.

    Returns:
        List of match-result dictionaries (one per application).
    """
    job_index = {j["job_id"]: j for j in jobs}
    results = []

    for app in applications:
        job_id = app.get("job_id")
        job = job_index.get(job_id)

        if job is None:
            results.append({
                "application_id": app.get("application_id", ""),
                "candidate_name": app.get("candidate_name", ""),
                "email":          app.get("email", ""),
                "job_id":         job_id,
                "job_title":      "Unknown",
                "qualified":      False,
                "missing_technologies": [],
                "missing_keywords":     [],
                "experience_gap":       0,
                "status":         "Regret",
                "warning":        f"Job '{job_id}' not found in job listings.",
            })
        else:
            results.append(match_application(app, job))

    return results
