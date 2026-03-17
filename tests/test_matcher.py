"""
Tests for the Application Tracker System.
"""

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.matcher import compute_match_score, determine_status, match_application, rank_applications
from src.models import Application, JobRequirement, MatchResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_job():
    return JobRequirement(
        job_id="J1",
        title="Python Developer",
        company="Acme",
        required_skills=["python", "sql", "rest api"],
        preferred_skills=["docker", "aws"],
        min_experience_years=2,
        location="Remote",
        description="Build APIs.",
    )


@pytest.fixture
def perfect_applicant():
    return Application(
        application_id="A1",
        applicant_name="Alice",
        email="alice@example.com",
        skills=["python", "sql", "rest api", "docker", "aws"],
        experience_years=5,
        location="Remote",
        resume_summary="Expert Python developer.",
    )


@pytest.fixture
def weak_applicant():
    return Application(
        application_id="A2",
        applicant_name="Bob",
        email="bob@example.com",
        skills=["javascript", "html"],
        experience_years=0,
        location="Remote",
        resume_summary="Junior frontend dev.",
    )


# ---------------------------------------------------------------------------
# compute_match_score
# ---------------------------------------------------------------------------

class TestComputeMatchScore:
    def test_perfect_match_returns_one(self, perfect_applicant, sample_job):
        score = compute_match_score(perfect_applicant, sample_job)
        assert score == 1.0

    def test_zero_overlap_returns_low_score(self, weak_applicant, sample_job):
        score = compute_match_score(weak_applicant, sample_job)
        assert score < 0.45

    def test_score_bounded_between_zero_and_one(self, perfect_applicant, sample_job):
        score = compute_match_score(perfect_applicant, sample_job)
        assert 0.0 <= score <= 1.0

    def test_partial_skill_match(self, sample_job):
        partial = Application(
            application_id="A3",
            applicant_name="Carol",
            email="carol@example.com",
            skills=["python", "sql"],
            experience_years=2,
            location="Remote",
            resume_summary="",
        )
        score = compute_match_score(partial, sample_job)
        assert 0.45 <= score < 1.0

    def test_experience_capped_at_one(self, sample_job):
        """Extra experience beyond minimum should not push score above 1."""
        overqualified = Application(
            application_id="A4",
            applicant_name="Dave",
            email="dave@example.com",
            skills=["python", "sql", "rest api", "docker", "aws"],
            experience_years=20,
            location="Remote",
            resume_summary="",
        )
        score = compute_match_score(overqualified, sample_job)
        assert score <= 1.0


# ---------------------------------------------------------------------------
# determine_status
# ---------------------------------------------------------------------------

class TestDetermineStatus:
    def test_accepted(self):
        assert determine_status(0.75) == "accepted"

    def test_waitlisted(self):
        assert determine_status(0.55) == "waitlisted"

    def test_rejected(self):
        assert determine_status(0.30) == "rejected"

    def test_boundary_accepted(self):
        assert determine_status(0.70) == "accepted"

    def test_boundary_waitlisted(self):
        assert determine_status(0.45) == "waitlisted"


# ---------------------------------------------------------------------------
# match_application
# ---------------------------------------------------------------------------

class TestMatchApplication:
    def test_returns_results_for_all_jobs(self, perfect_applicant, sample_job):
        jobs = [sample_job]
        results = match_application(perfect_applicant, jobs)
        assert len(results) == 1

    def test_results_sorted_descending(self, perfect_applicant):
        job1 = JobRequirement(
            job_id="J1", title="A", company="X",
            required_skills=["python"], preferred_skills=[],
            min_experience_years=1, location="Remote", description=""
        )
        job2 = JobRequirement(
            job_id="J2", title="B", company="Y",
            required_skills=["cobol", "fortran"], preferred_skills=[],
            min_experience_years=10, location="Remote", description=""
        )
        results = match_application(perfect_applicant, [job1, job2])
        scores = [r.match_score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_matched_and_missing_skills_populated(self, perfect_applicant, sample_job):
        results = match_application(perfect_applicant, [sample_job])
        assert set(results[0].matched_skills) == {"python", "rest api", "sql"}
        assert results[0].missing_skills == []


# ---------------------------------------------------------------------------
# rank_applications
# ---------------------------------------------------------------------------

class TestRankApplications:
    def test_ranking_order(self, perfect_applicant, weak_applicant, sample_job):
        ranked = rank_applications([weak_applicant, perfect_applicant], sample_job)
        assert ranked[0].applicant_name == "Alice"
        assert ranked[-1].applicant_name == "Bob"

    def test_empty_applications(self, sample_job):
        ranked = rank_applications([], sample_job)
        assert ranked == []
