# Application Tracker System

A Python-based system that automates the matching of job applications to job requirements, ranks candidates, and sends notifications based on match scores. Includes a **Flask web UI** for a full browser-based experience as well as a CLI.

## Features

- **Web UI** — Browser-based dashboard, job listings, applicant table, application form, and match results (Flask + Bootstrap 5)
- **Skill-based matching** — Compares candidate skills against required and preferred job skills with weighted scoring
- **Experience matching** — Factors in years of experience against job requirements
- **Candidate ranking** — Ranks multiple applicants for a single job best-first
- **Automated notifications** — Console-based (and optionally email-based) notifications for accepted, waitlisted, and rejected applicants
- **File-based logging** — Rotating log files and structured JSON event logs under `logs/`
- **Configurable thresholds** — Adjust accept/waitlist score cutoffs in `config.json`
- **CLI interface** — Flexible command-line options for different workflows

## Project Structure

```
application-tracker-system/
├── app.py                     # Flask web application
├── main.py                    # CLI entry point
├── config.json                # Configuration (thresholds, notification settings)
├── requirements.txt           # Python dependencies
├── src/
│   ├── __init__.py
│   ├── models.py              # Data classes (JobRequirement, Application, MatchResult)
│   ├── matcher.py             # Matching engine and ranking logic
│   ├── notifier.py            # Notification module
│   ├── logger.py              # File-based rotating logger
│   └── tracker.py             # Orchestration layer
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Shared layout (navbar, footer)
│   ├── index.html             # Dashboard
│   ├── jobs.html              # Job listings
│   ├── job_detail.html        # Single job + ranked applicants
│   ├── new_job.html           # Post a new job
│   ├── applications.html      # Application list
│   ├── apply.html             # Submit application form
│   └── results.html           # All match results with filter
├── static/
│   └── style.css              # Custom styles
├── data/
│   ├── job_requirements.json  # Sample job postings
│   ├── applications.json      # Sample applications
│   └── results.json           # Generated match results (auto-created)
├── logs/
│   ├── tracker.log            # Rotating application log (auto-created)
│   └── events.jsonl           # Structured event log (auto-created)
└── tests/
    └── test_matcher.py        # Unit tests for matching engine
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/ayush2309-wq/application-tracker-system.git
cd application-tracker-system
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the web UI

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | Stats overview + best match per applicant |
| Jobs | `/jobs` | All open positions (card grid) |
| Job Detail | `/jobs/<id>` | Job info + ranked applicants |
| Post a Job | `/jobs/new` | Form to add a new job posting |
| Applications | `/applications` | All applications table |
| Apply | `/applications/new` | Submit a new application |
| Results | `/results` | Full match matrix with status filter |

### 4. (Optional) Run the CLI

```bash
# Process all applications against all jobs (with notifications)
python main.py

# Rank applicants for a specific job
python main.py --rank-job JOB001

# Run without sending notifications
python main.py --no-notify

# Use custom data files
python main.py --jobs path/to/jobs.json --apps path/to/apps.json
```

## How Matching Works

Each application is scored against each job using a weighted formula:

| Component              | Weight |
|------------------------|--------|
| Required skills match  | 60 %   |
| Preferred skills match | 20 %   |
| Experience adequacy    | 20 %   |

The final score maps to a status:

| Score range  | Status      |
|--------------|-------------|
| ≥ 0.70       | ✅ Accepted  |
| 0.45 – 0.69  | ⏳ Waitlisted |
| < 0.45       | ❌ Rejected  |

Thresholds are configurable via `config.json`.

## Configuration

Edit `config.json` to adjust behavior:

```json
{
  "accept_threshold": 0.70,
  "waitlist_threshold": 0.45,
  "notifications": {
    "console": true,
    "email": false
  },
  "log_level": "INFO"
}
```

## Data Format

### Job Requirements (`data/job_requirements.json`)

```json
[
  {
    "job_id": "JOB001",
    "title": "Python Backend Developer",
    "company": "TechCorp Inc.",
    "required_skills": ["python", "django", "rest api", "sql"],
    "preferred_skills": ["docker", "aws", "redis"],
    "min_experience_years": 2,
    "location": "Remote",
    "description": "...",
    "posted_date": "2026-03-10"
  }
]
```

### Applications (`data/applications.json`)

```json
[
  {
    "application_id": "APP001",
    "applicant_name": "Alice Johnson",
    "email": "alice@example.com",
    "skills": ["python", "django", "rest api", "sql", "docker"],
    "experience_years": 4,
    "location": "Remote",
    "resume_summary": "...",
    "applied_date": "2026-03-16",
    "status": "pending"
  }
]
```

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
