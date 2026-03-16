"""
Notification module for the Application Tracker System.

Sends console/email-style notifications for application decisions.
Currently supports console output; extend _send_email for real SMTP delivery.
"""

from typing import Optional

from .logger import get_logger, log_event
from .models import MatchResult

logger = get_logger("notifier")

_TEMPLATES = {
    "accepted": (
        "Congratulations, {name}! "
        "Your application (ID: {app_id}) has been ACCEPTED for the role of "
        "{title} at {company} with a match score of {score:.0%}."
    ),
    "waitlisted": (
        "Dear {name}, "
        "Your application (ID: {app_id}) for {title} at {company} has been "
        "WAITLISTED (match score: {score:.0%}). "
        "We will contact you if a position becomes available."
    ),
    "rejected": (
        "Dear {name}, "
        "We regret to inform you that your application (ID: {app_id}) for "
        "{title} at {company} was not selected at this time "
        "(match score: {score:.0%}). "
        "Missing skills: {missing}. "
        "We encourage you to apply again in the future."
    ),
}


def _format_message(result: MatchResult) -> str:
    template = _TEMPLATES.get(result.status, "Application status updated.")
    return template.format(
        name=result.applicant_name,
        app_id=result.application_id,
        title=result.job_title,
        company=result.company,
        score=result.match_score,
        missing=", ".join(result.missing_skills) if result.missing_skills else "none",
    )


def _send_email(to_email: Optional[str], subject: str, body: str) -> None:
    """Placeholder for SMTP integration. Logs the email payload."""
    if to_email:
        logger.debug("EMAIL to %s | Subject: %s | Body: %s", to_email, subject, body)
    else:
        logger.debug("No email address provided; skipping email delivery.")


def notify(result: MatchResult, email: Optional[str] = None) -> None:
    """
    Notify a candidate about their application decision.

    Logs the notification and optionally sends an email.
    """
    message = _format_message(result)
    logger.info("[NOTIFY] %s", message)

    log_event(
        "notification_sent",
        {
            "application_id": result.application_id,
            "job_id": result.job_id,
            "status": result.status,
            "match_score": result.match_score,
        },
    )

    subject = f"Application Update: {result.job_title} at {result.company}"
    _send_email(email, subject, message)


def notify_all(results: list, emails: Optional[dict] = None) -> None:
    """
    Send notifications for a list of MatchResult objects.

    :param results: List[MatchResult]
    :param emails:  Optional dict mapping application_id -> email address
    """
    emails = emails or {}
    for result in results:
        notify(result, email=emails.get(result.application_id))
