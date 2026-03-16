"""
Matching engine for the Application Tracker System.

Computes a weighted match score between an application and a job requirement,
then ranks and filters candidates.
"""

from typing import List, Tuple

from .models import Application, JobRequirement, MatchResult

# Score thresholds
ACCEPT_THRESHOLD = 0.70
WAITLIST_THRESHOLD = 0.45


def _skill_overlap(candidate_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str]]:
    """Return (matched_skills, missing_skills) comparing lower-cased sets."""
    candidate_set = {s.lower() for s in candidate_skills}
    job_set = {s.lower() for s in job_skills}
    matched = sorted(candidate_set & job_set)
    missing = sorted(job_set - candidate_set)
    return matched, missing


def compute_match_score(application: Application, job: JobRequirement) -> float:
    """
    Calculate a match score in [0, 1] based on:
      - Required skills coverage (60 % weight)
      - Preferred skills coverage (20 % weight)
      - Experience adequacy       (20 % weight)
    """
    # Required skills
    req_matched, _ = _skill_overlap(application.skills, job.required_skills)
    req_score = len(req_matched) / len(job.required_skills) if job.required_skills else 1.0

    # Preferred skills
    if job.preferred_skills:
        pref_matched, _ = _skill_overlap(application.skills, job.preferred_skills)
        pref_score = len(pref_matched) / len(job.preferred_skills)
    else:
        pref_score = 1.0

    # Experience
    if job.min_experience_years > 0:
        exp_score = min(application.experience_years / job.min_experience_years, 1.0)
    else:
        exp_score = 1.0

    return round(0.60 * req_score + 0.20 * pref_score + 0.20 * exp_score, 4)


def determine_status(score: float) -> str:
    """Map a numeric score to an application status string."""
    if score >= ACCEPT_THRESHOLD:
        return "accepted"
    if score >= WAITLIST_THRESHOLD:
        return "waitlisted"
    return "rejected"


def match_application(application: Application, jobs: List[JobRequirement]) -> List[MatchResult]:
    """
    Match a single application against all provided jobs.

    Returns a list of MatchResult objects sorted by match_score descending.
    """
    results: List[MatchResult] = []

    for job in jobs:
        score = compute_match_score(application, job)
        matched_skills, missing_skills = _skill_overlap(application.skills, job.required_skills)
        status = determine_status(score)

        results.append(
            MatchResult(
                application_id=application.application_id,
                job_id=job.job_id,
                applicant_name=application.applicant_name,
                job_title=job.title,
                company=job.company,
                match_score=score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                status=status,
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results


def rank_applications(applications: List[Application], job: JobRequirement) -> List[MatchResult]:
    """
    Rank all applicants for a single job by match score.

    Returns results sorted best-first.
    """
    results: List[MatchResult] = []

    for app in applications:
        score = compute_match_score(app, job)
        matched_skills, missing_skills = _skill_overlap(app.skills, job.required_skills)
        status = determine_status(score)

        results.append(
            MatchResult(
                application_id=app.application_id,
                job_id=job.job_id,
                applicant_name=app.applicant_name,
                job_title=job.title,
                company=job.company,
                match_score=score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                status=status,
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results
