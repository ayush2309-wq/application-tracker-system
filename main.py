#!/usr/bin/env python3
"""
main.py – CLI runner for the Application Tracker System.

Usage
-----
    python main.py                          # use bundled example data
    python main.py --jobs path/to/jobs.json --applications path/to/apps.json
    python main.py --summary-only           # print summary table only
    python main.py --help

No external dependencies – only the Python standard library is required.
"""

import argparse
import os
import sys

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_jobs, load_applications
from src.matcher import run_matching
from src.notifier import send_notifications
from src.logger import log_run_start, log_all_results, log_run_summary


_DEFAULT_JOBS_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.json")
_DEFAULT_APPS_PATH = os.path.join(os.path.dirname(__file__), "data", "applications.json")


def print_summary_table(results: list) -> None:
    """Print a formatted summary table of all match results."""
    col_widths = {
        "app_id":    14,
        "name":      20,
        "job_title": 24,
        "status":    13,
    }

    header = (
        f"{'App ID':<{col_widths['app_id']}} "
        f"{'Candidate':<{col_widths['name']}} "
        f"{'Job Title':<{col_widths['job_title']}} "
        f"{'Status':<{col_widths['status']}}"
    )
    divider = "-" * len(header)

    print("\n" + "=" * len(header))
    print("  MATCHING RESULTS SUMMARY")
    print("=" * len(header))
    print(header)
    print(divider)

    for r in results:
        status_display = "✔ Move Forward" if r["qualified"] else "✘ Regret"
        print(
            f"{r['application_id']:<{col_widths['app_id']}} "
            f"{r['candidate_name']:<{col_widths['name']}} "
            f"{r['job_title']:<{col_widths['job_title']}} "
            f"{status_display:<{col_widths['status']}}"
        )

    print(divider)
    total    = len(results)
    advanced = sum(1 for r in results if r["qualified"])
    print(
        f"\nTotal applications: {total}  |  "
        f"Move Forward: {advanced}  |  "
        f"Regret: {total - advanced}\n"
    )


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Application Tracker System – matches candidates to job requirements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py\n"
            "  python main.py --jobs data/jobs.json --applications data/applications.json\n"
            "  python main.py --summary-only\n"
        ),
    )
    parser.add_argument(
        "--jobs",
        default=_DEFAULT_JOBS_PATH,
        metavar="FILE",
        help="Path to the jobs JSON file (default: data/jobs.json)",
    )
    parser.add_argument(
        "--applications",
        default=_DEFAULT_APPS_PATH,
        metavar="FILE",
        help="Path to the applications JSON file (default: data/applications.json)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary table; suppress individual notifications.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Entry point.  Returns exit code (0 = success)."""
    args = parse_args(argv)

    # ── 1. Load data ──────────────────────────────────────────────────────────
    print(f"\nLoading jobs from        : {args.jobs}")
    print(f"Loading applications from: {args.applications}")

    try:
        jobs         = load_jobs(args.jobs)
        applications = load_applications(args.applications)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    print(f"\n  Loaded {len(jobs)} job(s) and {len(applications)} application(s).\n")

    # ── 2. Log run start ──────────────────────────────────────────────────────
    log_run_start(len(jobs), len(applications))

    # ── 3. Run matching ───────────────────────────────────────────────────────
    results = run_matching(applications, jobs)

    # ── 4. Log results ────────────────────────────────────────────────────────
    log_all_results(results)
    log_run_summary(results)

    # ── 5. Send notifications (unless --summary-only) ─────────────────────────
    if not args.summary_only:
        send_notifications(results)

    # ── 6. Print summary table ────────────────────────────────────────────────
    print_summary_table(results)

    logs_path = os.path.join(os.path.dirname(__file__), "logs", "tracker.log")
    print(f"Detailed log written to  : {logs_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
