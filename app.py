"""
Flask web frontend for the Application Tracker System.

Routes:
  GET  /                       Dashboard
  GET  /jobs                   Job listings
  GET  /jobs/<job_id>          Job detail + ranked applicants
  GET  /applications           Application list
  GET  /applications/new       New-application form
  POST /applications/new       Submit new application
  GET  /results                Run matching & view all results
  POST /results/run            Re-run matching (JSON API)
"""

import json
import os
import uuid
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from src.logger import get_logger
from src.matcher import match_application, rank_applications
from src.models import Application, JobRequirement
from src.tracker import (
    load_applications,
    load_job_requirements,
    process_applications,
    rank_for_job,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

logger = get_logger("web")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
JOBS_FILE = os.path.join(DATA_DIR, "job_requirements.json")
APPS_FILE = os.path.join(DATA_DIR, "applications.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_jobs() -> list:
    return load_job_requirements(JOBS_FILE)


def _load_apps() -> list:
    return load_applications(APPS_FILE)


def _save_applications(applications: list) -> None:
    """Persist the full list of Application objects back to the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    serializable = [a.__dict__ for a in applications]
    with open(APPS_FILE, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, indent=2)


def _save_jobs(jobs: list) -> None:
    """Persist the full list of JobRequirement objects back to the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    serializable = [j.__dict__ for j in jobs]
    with open(JOBS_FILE, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, indent=2)


def _status_badge(status: str) -> str:
    mapping = {
        "accepted": "success",
        "waitlisted": "warning",
        "rejected": "danger",
        "pending": "secondary",
    }
    return mapping.get(status, "secondary")


# Make the badge helper available in all templates.
app.jinja_env.globals["status_badge"] = _status_badge


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    jobs = _load_jobs()
    applications = _load_apps()

    results = process_applications(applications, jobs, notify=False)

    stats = {
        "total_jobs": len(jobs),
        "total_applications": len(applications),
        "accepted": sum(1 for r in results if r.status == "accepted"),
        "waitlisted": sum(1 for r in results if r.status == "waitlisted"),
        "rejected": sum(1 for r in results if r.status == "rejected"),
    }

    # Only show the best result per applicant for the summary table.
    seen = set()
    best_results = []
    for r in results:
        if r.application_id not in seen:
            best_results.append(r)
            seen.add(r.application_id)

    return render_template("index.html", stats=stats, results=best_results, jobs=jobs)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

@app.route("/jobs")
def jobs():
    jobs_list = _load_jobs()
    return render_template("jobs.html", jobs=jobs_list)


@app.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    if request.method == "POST":
        f = request.form
        required_skills = [s.strip().lower() for s in f["required_skills"].split(",") if s.strip()]
        preferred_skills = [s.strip().lower() for s in f.get("preferred_skills", "").split(",") if s.strip()]
        try:
            min_exp = int(f.get("min_experience_years", 0))
        except ValueError:
            min_exp = 0

        job = JobRequirement(
            job_id=f"JOB{str(uuid.uuid4())[:6].upper()}",
            title=f["title"].strip(),
            company=f["company"].strip(),
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience_years=min_exp,
            location=f.get("location", "").strip(),
            description=f.get("description", "").strip(),
            posted_date=datetime.now().strftime("%Y-%m-%d"),
        )
        jobs_list = _load_jobs()
        jobs_list.append(job)
        _save_jobs(jobs_list)
        flash(f"Job '{job.title}' posted successfully!", "success")
        return redirect(url_for("jobs"))

    return render_template("new_job.html")


@app.route("/jobs/<job_id>")
def job_detail(job_id):
    jobs_list = _load_jobs()
    job = next((j for j in jobs_list if j.job_id == job_id), None)
    if job is None:
        flash(f"Job '{job_id}' not found.", "danger")
        return redirect(url_for("jobs"))

    applications = _load_apps()
    ranked = rank_applications(applications, job)
    return render_template("job_detail.html", job=job, ranked=ranked)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@app.route("/applications")
def applications():
    apps = _load_apps()
    jobs = _load_jobs()
    job_map = {j.job_id: j.title for j in jobs}
    return render_template("applications.html", applications=apps, job_map=job_map)


@app.route("/applications/new", methods=["GET", "POST"])
def new_application():
    jobs_list = _load_jobs()

    if request.method == "POST":
        f = request.form
        skills = [s.strip().lower() for s in f["skills"].split(",") if s.strip()]
        try:
            experience_years = int(f.get("experience_years", 0))
        except ValueError:
            experience_years = 0

        new_app = Application(
            application_id=f"APP{str(uuid.uuid4())[:6].upper()}",
            applicant_name=f["applicant_name"].strip(),
            email=f["email"].strip(),
            skills=skills,
            experience_years=experience_years,
            location=f.get("location", "").strip(),
            resume_summary=f.get("resume_summary", "").strip(),
            applied_date=datetime.now().strftime("%Y-%m-%d"),
            status="pending",
        )
        apps = _load_apps()
        apps.append(new_app)
        _save_applications(apps)
        logger.info("New application submitted: %s (%s)", new_app.application_id, new_app.applicant_name)
        flash(f"Application submitted successfully! Your ID is {new_app.application_id}.", "success")
        return redirect(url_for("applications"))

    return render_template("apply.html", jobs=jobs_list)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

@app.route("/results")
def results():
    jobs = _load_jobs()
    applications = _load_apps()
    all_results = process_applications(applications, jobs, notify=False)
    return render_template("results.html", results=all_results, total=len(all_results))


@app.route("/results/run", methods=["POST"])
def run_matching():
    """JSON endpoint to re-trigger matching (used by the results page button)."""
    jobs = _load_jobs()
    applications = _load_apps()
    results = process_applications(applications, jobs, notify=False)
    return jsonify({"status": "ok", "count": len(results)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
