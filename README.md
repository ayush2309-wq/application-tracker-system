# Application Tracker System

A modular, command-line Python application that matches job seekers against job requirements and automatically sends "Move Forward" or "Regret" notifications — with full audit logging.

No external dependencies are required; only the Python standard library is used.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Data Format](#data-format)
- [Module Overview](#module-overview)
- [Logging](#logging)
- [Extending the System](#extending-the-system)

---

## Features

- Loads job requirements and candidate applications from JSON files.
- Matches each application against its target job on:
  - **Technologies** – all required technologies must be present.
  - **Keywords** – all required keywords must be present.
  - **Experience** – candidate must meet the minimum years of experience.
- Prints a personalized **Move Forward** notification for qualified candidates.
- Prints a detailed **Regret** notification (with gap feedback) for others.
- Writes structured audit logs to `logs/tracker.log`.
- Fully modular codebase with separate files for each concern.

---

## Project Structure

```
application-tracker-system/
├── data/
│   ├── jobs.json            # Job requirements
│   └── applications.json    # Candidate applications
├── src/
│   ├── __init__.py          # Package public API
│   ├── data_loader.py       # JSON data loading
│   ├── matcher.py           # Matching logic
│   ├── notifier.py          # Notification generation
│   └── logger.py            # Audit/tracking logger
├── logs/
│   └── tracker.log          # Generated at runtime
├── main.py                  # CLI runner
└── README.md
```

---

## Setup

1. **Python 3.8 or newer** is required (no third-party packages needed).

2. Clone the repository:
   ```bash
   git clone https://github.com/ayush2309-wq/application-tracker-system.git
   cd application-tracker-system
   ```

3. *(Optional)* Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

That's it — no `pip install` step is required.

---

## Usage

### Run with bundled example data

```bash
python main.py
```

This loads `data/jobs.json` and `data/applications.json`, runs the matcher, prints all notifications, displays a summary table, and writes an audit log to `logs/tracker.log`.

### Run with custom data files

```bash
python main.py --jobs path/to/jobs.json --applications path/to/apps.json
```

### Print only the summary table (suppress per-candidate notifications)

```bash
python main.py --summary-only
```

### Show help

```bash
python main.py --help
```

### Expected output (excerpt)

```
Loading jobs from        : .../data/jobs.json
Loading applications from: .../data/applications.json

  Loaded 4 job(s) and 8 application(s).

============================================================
  NOTIFICATION  |  Status: Move Forward
============================================================
Dear Alice Johnson,

Congratulations! After reviewing your application (ID: A001) for the
position of Backend Developer (Job ID: J001), we are pleased to inform
you that you have been shortlisted to MOVE FORWARD ...
...

==========================================================================
  MATCHING RESULTS SUMMARY
==========================================================================
App ID         Candidate            Job Title                Status
--------------------------------------------------------------------------
A001           Alice Johnson        Backend Developer        ✔ Move Forward
A002           Bob Smith            Backend Developer        ✘ Regret
...
--------------------------------------------------------------------------

Total applications: 8  |  Move Forward: 4  |  Regret: 4
```

---

## Data Format

### `data/jobs.json`

```json
[
  {
    "job_id": "J001",
    "title": "Backend Developer",
    "required_technologies": ["Python", "Django", "PostgreSQL"],
    "required_keywords": ["REST API", "microservices"],
    "min_experience_years": 2
  }
]
```

| Field                    | Type     | Description                                  |
|--------------------------|----------|----------------------------------------------|
| `job_id`                 | string   | Unique identifier for the job                |
| `title`                  | string   | Human-readable job title                     |
| `required_technologies`  | string[] | All technologies a candidate must know       |
| `required_keywords`      | string[] | All keywords a candidate must mention        |
| `min_experience_years`   | integer  | Minimum years of experience required         |

### `data/applications.json`

```json
[
  {
    "application_id": "A001",
    "job_id": "J001",
    "candidate_name": "Alice Johnson",
    "email": "alice@example.com",
    "technologies": ["Python", "Django", "PostgreSQL", "Redis"],
    "keywords": ["REST API", "microservices", "Docker"],
    "experience_years": 3
  }
]
```

| Field              | Type     | Description                                    |
|--------------------|----------|------------------------------------------------|
| `application_id`   | string   | Unique identifier for the application          |
| `job_id`           | string   | Target job (must match a `job_id` in jobs.json)|
| `candidate_name`   | string   | Full name of the candidate                     |
| `email`            | string   | Candidate's email address                      |
| `technologies`     | string[] | Technologies the candidate knows               |
| `keywords`         | string[] | Keywords from the candidate's profile          |
| `experience_years` | integer  | Years of relevant experience                   |

---

## Module Overview

| Module                | Responsibility                                                  |
|-----------------------|-----------------------------------------------------------------|
| `src/data_loader.py`  | Reads and validates JSON data files                            |
| `src/matcher.py`      | Compares applications to job requirements; returns results     |
| `src/notifier.py`     | Composes and emits Move Forward / Regret notification messages |
| `src/logger.py`       | Writes structured audit entries to `logs/tracker.log`          |
| `main.py`             | CLI entry point – orchestrates the full workflow               |

---

## Logging

Every run appends structured entries to `logs/tracker.log`:

```
2026-03-16 14:54:48 | INFO     | === Matching run started | jobs=4 | applications=8 ===
2026-03-16 14:54:48 | INFO     | MOVE FORWARD | app=A001 | candidate=Alice Johnson | job=J001 (Backend Developer)
2026-03-16 14:54:48 | WARNING  | REGRET       | app=A002 | candidate=Bob Smith | job=J001 (Backend Developer) | missing_tech=['django', 'postgresql'] | missing_kw=['microservices'] | exp_gap=1
...
2026-03-16 14:54:48 | INFO     | === Run summary | total=8 | move_forward=4 | regret=4 ===
```

`INFO` entries record successful "Move Forward" decisions; `WARNING` entries record rejections with the reasons.

---

## Extending the System

- **Add a new job or application** – edit the corresponding JSON file.
- **Send real emails** – replace the `output_fn` in `notifier.send_notifications` with an `smtplib`-based function.
- **Persist results to a database** – add a `db.py` module that writes the result dicts from `matcher.run_matching`.
- **Build a REST API** – wrap `main()` logic with Flask or FastAPI routes.
- **Score-based ranking** – extend `matcher.match_application` to return a numeric score instead of a binary pass/fail.
