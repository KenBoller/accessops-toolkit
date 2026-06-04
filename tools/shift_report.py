"""
AccessOps Toolkit - Shift Report Generator
------------------------------------------
Generates a mock SOC/Operations shift handoff report using local JSON data.

This tool summarizes:
- Open tickets
- Triggered incidents
- Active bridge calls
- Recent notifications
- Access changes
- New hire onboarding activity

Outputs:
- Console summary
- Markdown report file

Example:
    python tools/shift_report.py
    python tools/shift_report.py --save-only
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
REPORTS_DIR = PROJECT_DIR / "reports"
LOG_DIR = PROJECT_DIR / "logs"

TICKETS_FILE = DATA_DIR / "tickets.json"
INCIDENTS_FILE = DATA_DIR / "incidents.json"
BRIDGES_FILE = DATA_DIR / "bridges.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
ACCESS_STATE_FILE = DATA_DIR / "access_state.json"
NEW_HIRES_FILE = DATA_DIR / "new_hires.json"

LOG_FILE = LOG_DIR / "shift_report.log"

REPORTS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_json(path: Path, default):
    """Safely load JSON data."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in %s", path)
        return default


def current_timestamp() -> str:
    """Return formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_open_tickets(ticket_data: dict) -> list:
    """Return open tickets."""
    return [
        ticket
        for ticket in ticket_data.get("tickets", [])
        if ticket.get("status") == "open"
    ]


def get_triggered_incidents(incident_data: dict) -> list:
    """Return triggered incidents."""
    return [
        incident
        for incident in incident_data.get("incidents", [])
        if incident.get("status") == "triggered"
    ]


def get_active_bridges(bridge_data: dict) -> list:
    """Return active bridge calls."""
    return [
        bridge
        for bridge in bridge_data.get("bridges", [])
        if bridge.get("status") == "open"
    ]


def get_recent_notifications(notification_data: dict, hours: int = 24) -> list:
    """Return recent notifications."""
    cutoff = datetime.now() - timedelta(hours=hours)

    results = []

    for notification in notification_data.get("notifications", []):
        try:
            created = datetime.fromisoformat(notification["created_at"])

            if created >= cutoff:
                results.append(notification)

        except Exception:
            continue

    return results


def summarize_access_changes(access_data: dict) -> tuple[int, int]:
    """
    Count access grants/removals.

    Returns:
        tuple(grants, removals)
    """
    grants = 0
    removals = 0

    for system_data in access_data.values():
        for user_data in system_data.values():
            if user_data.get("enabled"):
                grants += 1

            if user_data.get("removed_at"):
                removals += 1

    return grants, removals


def get_completed_onboarding_count(new_hire_data: dict) -> int:
    """Count completed onboarding records."""
    return len(
        [
            hire
            for hire in new_hire_data.get("new_hires", [])
            if hire.get("status") == "completed"
        ]
    )


def generate_report() -> str:
    """Generate the markdown shift report."""

    ticket_data = load_json(TICKETS_FILE, {"tickets": []})
    incident_data = load_json(INCIDENTS_FILE, {"incidents": []})
    bridge_data = load_json(BRIDGES_FILE, {"bridges": []})
    notification_data = load_json(NOTIFICATIONS_FILE, {"notifications": []})
    access_data = load_json(ACCESS_STATE_FILE, {})
    new_hire_data = load_json(NEW_HIRES_FILE, {"new_hires": []})

    open_tickets = get_open_tickets(ticket_data)
    incidents = get_triggered_incidents(incident_data)
    bridges = get_active_bridges(bridge_data)
    notifications = get_recent_notifications(notification_data)

    grants, removals = summarize_access_changes(access_data)

    completed_onboarding = get_completed_onboarding_count(new_hire_data)

    timestamp = current_timestamp()

    report = f"""# AccessOps Toolkit - Shift Report

Generated: {timestamp}

---

## Summary

| Metric | Count |
|---|---|
| Open Tickets | {len(open_tickets)} |
| Triggered Incidents | {len(incidents)} |
| Active Bridge Calls | {len(bridges)} |
| Recent Notifications | {len(notifications)} |
| Active Access Grants | {grants} |
| Access Removals | {removals} |
| Completed Onboardings | {completed_onboarding} |

---

## Open Tickets
"""

    if open_tickets:
        for ticket in open_tickets:
            report += (
                f"- #{ticket.get('id')} | "
                f"{ticket.get('title')} | "
                f"Assigned: {ticket.get('assigned_to', 'unassigned')}\n"
            )
    else:
        report += "- None\n"

    report += "\n---\n\n## Triggered Incidents\n"

    if incidents:
        for incident in incidents:
            report += (
                f"- Incident #{incident.get('id')} | "
                f"{incident.get('title')} | "
                f"Severity: {incident.get('severity')}\n"
            )
    else:
        report += "- None\n"

    report += "\n---\n\n## Active Bridge Calls\n"

    if bridges:
        for bridge in bridges:
            report += (
                f"- Bridge #{bridge.get('id')} | "
                f"{bridge.get('bridge_url')}\n"
            )
    else:
        report += "- None\n"

    report += "\n---\n\n## Recent Notifications\n"

    if notifications:
        for notification in notifications[-5:]:
            report += (
                f"- [{notification.get('severity')}] "
                f"{notification.get('message')}\n"
            )
    else:
        report += "- None\n"

    report += "\n---\n\n## End of Report\n"

    return report


def save_report(report: str) -> Path:
    """Save report to markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = REPORTS_DIR / f"shift_report_{timestamp}.md"

    with report_path.open("w", encoding="utf-8") as file:
        file.write(report)

    latest_report = REPORTS_DIR / "latest_shift_report.md"

    with latest_report.open("w", encoding="utf-8") as file:
        file.write(report)

    return report_path


def parse_arguments():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Generate a shift handoff report.")

    parser.add_argument(
        "--save-only",
        action="store_true",
        help="Save report without printing to console.",
    )

    return parser.parse_args()


def main():
    """Run shift report generator."""
    args = parse_arguments()

    report = generate_report()

    report_path = save_report(report)

    logging.info("Generated shift report: %s", report_path)

    if not args.save_only:
        print(report)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()