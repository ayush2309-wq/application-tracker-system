"""
Application data models for the Application Tracker System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class JobRequirement:
    """Represents a job opening with its requirements."""

    job_id: str
    title: str
    company: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: int
    location: str
    description: str
    posted_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class Application:
    """Represents a job application submitted by a candidate."""

    application_id: str
    applicant_name: str
    email: str
    skills: List[str]
    experience_years: int
    location: str
    resume_summary: str
    applied_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    status: str = "pending"
    matched_job_id: Optional[str] = None
    match_score: float = 0.0

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class MatchResult:
    """Holds the result of matching an application to a job."""

    application_id: str
    job_id: str
    applicant_name: str
    job_title: str
    company: str
    match_score: float
    matched_skills: List[str]       # required skills matched
    missing_skills: List[str]       # required skills missing
    status: str                     # "accepted", "waitlisted", "rejected"

    # Per-component scores (0 – 1)
    req_score: float = 0.0          # required-skills component
    pref_score: float = 0.0         # preferred-skills component
    exp_score: float = 0.0          # experience component

    # Preferred-skill detail
    preferred_matched: List[str] = field(default_factory=list)
    preferred_missing: List[str] = field(default_factory=list)
