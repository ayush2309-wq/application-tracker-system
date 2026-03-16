"""
notifier.py – Sends (mocked) notifications to candidates based on match results.

In a production system, this module would send emails or push notifications.
For this demonstration, notifications are printed to stdout and can also be
written to a log file via the logger module.
"""

from typing import Dict, List, Callable


def _build_move_forward_message(result: Dict) -> str:
    """Compose the 'Move Forward' notification message."""
    return (
        f"Dear {result['candidate_name']},\n\n"
        f"Congratulations! After reviewing your application (ID: {result['application_id']}) "
        f"for the position of {result['job_title']} (Job ID: {result['job_id']}), "
        f"we are pleased to inform you that you have been shortlisted to MOVE FORWARD "
        f"in our recruitment process.\n\n"
        f"We will be in touch shortly with next steps.\n\n"
        f"Best regards,\nThe Recruitment Team"
    )


def _build_regret_message(result: Dict) -> str:
    """Compose the regret notification message with brief feedback."""
    reasons = []
    if result.get("missing_technologies"):
        reasons.append(
            "missing technologies: " + ", ".join(result["missing_technologies"])
        )
    if result.get("missing_keywords"):
        reasons.append(
            "missing keywords: " + ", ".join(result["missing_keywords"])
        )
    if result.get("experience_gap", 0) > 0:
        reasons.append(
            f"insufficient experience ({result['experience_gap']} year(s) below requirement)"
        )

    feedback = (
        "  Reasons: " + "; ".join(reasons) + "."
        if reasons
        else "  Your profile did not fully match the role requirements at this time."
    )

    return (
        f"Dear {result['candidate_name']},\n\n"
        f"Thank you for your application (ID: {result['application_id']}) "
        f"for the position of {result['job_title']} (Job ID: {result['job_id']}).\n\n"
        f"After careful consideration, we regret to inform you that we will not be "
        f"moving forward with your application at this time.\n"
        f"{feedback}\n\n"
        f"We wish you all the best in your job search.\n\n"
        f"Best regards,\nThe Recruitment Team"
    )


def compose_notification(result: Dict) -> str:
    """Return the appropriate notification message for a match result.

    Args:
        result: A match-result dictionary produced by matcher.match_application.

    Returns:
        Formatted notification string.
    """
    if result.get("qualified"):
        return _build_move_forward_message(result)
    return _build_regret_message(result)


def send_notifications(
    results: List[Dict],
    output_fn: Callable[[str], None] = print,
) -> List[Dict]:
    """Send notifications for every match result.

    Args:
        results:   List of match-result dicts from the matcher.
        output_fn: Function used to emit each notification (default: print).
                   Useful for capturing output in tests or logging pipelines.

    Returns:
        List of notification records, each containing:
            - application_id (str)
            - candidate_name (str)
            - email (str)
            - status (str)
            - message (str)
    """
    notifications = []

    for result in results:
        message = compose_notification(result)
        separator = "=" * 60
        output_fn(separator)
        output_fn(f"  NOTIFICATION  |  Status: {result['status']}")
        output_fn(separator)
        output_fn(message)
        output_fn("")

        notifications.append({
            "application_id": result["application_id"],
            "candidate_name": result["candidate_name"],
            "email": result["email"],
            "status": result["status"],
            "message": message,
        })

    return notifications
