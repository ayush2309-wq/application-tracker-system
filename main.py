"""
Main entry point for the Application Tracker System CLI.

Usage:
    python main.py                          # Process all applications against all jobs
    python main.py --rank-job JOB001        # Rank applicants for a specific job
    python main.py --no-notify              # Skip sending notifications
    python main.py --jobs path/to/jobs.json # Use a custom jobs file
    python main.py --apps path/to/apps.json # Use a custom applications file
"""

import argparse
import json
import sys

from src.logger import get_logger
from src.tracker import load_applications, load_job_requirements, process_applications, rank_for_job

logger = get_logger("main")


def _print_results(results: list) -> None:
    """Pretty-print match results to stdout."""
    if not results:
        print("No results to display.")
        return

    print("\n" + "=" * 70)
    print(f"{'APPLICANT':<25} {'JOB':<28} {'SCORE':>6}  {'STATUS'}")
    print("-" * 70)
    for r in results:
        print(
            f"{r.applicant_name:<25} {r.job_title:<28} {r.match_score:>5.0%}  {r.status.upper()}"
        )
    print("=" * 70 + "\n")


def _load_config(path: str = "config.json") -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Application Tracker System — match applicants to job requirements."
    )
    parser.add_argument("--jobs", default=None, help="Path to job requirements JSON file.")
    parser.add_argument("--apps", default=None, help="Path to applications JSON file.")
    parser.add_argument(
        "--rank-job",
        metavar="JOB_ID",
        default=None,
        help="Rank all applicants for the specified job ID.",
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="Disable sending notifications.",
    )
    args = parser.parse_args()

    config = _load_config()
    logger.info("Application Tracker System starting.")

    try:
        jobs = load_job_requirements(args.jobs)
        applications = load_applications(args.apps)
    except FileNotFoundError as exc:
        logger.error("Data file not found: %s", exc)
        return 1

    if args.rank_job:
        results = rank_for_job(args.rank_job, applications, jobs)
        print(f"\nRankings for Job ID: {args.rank_job}")
    else:
        send_notify = not args.no_notify and config.get("notifications", {}).get("console", True)
        results = process_applications(applications, jobs, notify=send_notify)

    _print_results(results)
    logger.info("Done. Processed %d result(s).", len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
