"""
AccessOps Toolkit - Alert Handler
---------------------------------
Portfolio-safe mock alert ingestion and escalation workflow.

This script:
- Reads mock alerts from data/alerts.json
- Detects high-severity alerts
- Creates mock tickets in data/tickets.json
- Creates mock incident records in data/incidents.json
- Supports dry-run mode for safe testing

Example usage:
    python tools/alert_handler.py
    python tools/alert_handler.py --dry-run
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

ALERTS_FILE = DATA_DIR / "alerts.json"
INCIDENTS_FILE = DATA_DIR / "incidents.json"
LOG_FILE = LOG_DIR / "alert_handler.log"

HIGH_SEVERITIES = {"critical", "major", "sev0", "sev1", "sev2"}

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.ticket_manager import load_ticket_data, save_ticket_data, now


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_alerts() -> dict:
    """Load mock alerts from data/alerts.json."""
    if not ALERTS_FILE.exists():
        return {"alerts": []}

    try:
        with ALERTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("alerts.json contains invalid JSON.")
        return {"alerts": []}


def load_incidents() -> dict:
    """Load mock incidents from data/incidents.json."""
    if not INCIDENTS_FILE.exists():
        return {"incidents": []}

    try:
        with INCIDENTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("incidents.json contains invalid JSON.")
        return {"incidents": []}


def save_incidents(incident_data: dict) -> None:
    """Save mock incidents to data/incidents.json."""
    with INCIDENTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(incident_data, file, indent=2)


def is_high_severity(alert: dict) -> bool:
    """Return True if an alert should create a ticket and incident."""
    severity = str(alert.get("severity", "")).lower()
    return severity in HIGH_SEVERITIES


def get_next_ticket_id(ticket_data: dict) -> int:
    """Generate the next mock ticket ID."""
    tickets = ticket_data.get("tickets", [])

    if not tickets:
        return 1001

    return max(int(ticket.get("id", 1000)) for ticket in tickets) + 1


def get_next_incident_id(incident_data: dict) -> int:
    """Generate the next mock incident ID."""
    incidents = incident_data.get("incidents", [])

    if not incidents:
        return 5001

    return max(int(incident.get("id", 5000)) for incident in incidents) + 1


def ticket_already_exists_for_alert(ticket_data: dict, alert_id: str) -> bool:
    """Prevent duplicate tickets for the same alert."""
    for ticket in ticket_data.get("tickets", []):
        if ticket.get("source_alert_id") == alert_id:
            return True

    return False


def incident_already_exists_for_alert(incident_data: dict, alert_id: str) -> bool:
    """Prevent duplicate incidents for the same alert."""
    for incident in incident_data.get("incidents", []):
        if incident.get("source_alert_id") == alert_id:
            return True

    return False


def create_ticket_from_alert(alert: dict, ticket_data: dict) -> dict:
    """Create a mock ticket record from an alert."""
    timestamp = now()
    ticket_id = get_next_ticket_id(ticket_data)

    title = alert.get("title") or alert.get("text") or "Untitled alert"
    severity = alert.get("severity", "unknown")
    system = alert.get("system", "unknown")

    ticket = {
        "id": ticket_id,
        "title": title,
        "status": "open",
        "queue": "alerts",
        "severity": severity,
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_to": "automation",
        "system": system,
        "source_alert_id": alert.get("id"),
        "history": [
            {
                "timestamp": timestamp,
                "type": "alert",
                "message": alert.get("text", title),
            },
            {
                "timestamp": timestamp,
                "type": "automation",
                "message": "Ticket created automatically from high-severity alert.",
            },
        ],
    }

    ticket_data.setdefault("tickets", []).append(ticket)
    return ticket


def create_incident_from_alert(alert: dict, incident_data: dict, ticket_id: int) -> dict:
    """Create a mock incident escalation record from an alert."""
    timestamp = now()
    incident_id = get_next_incident_id(incident_data)

    incident = {
        "id": incident_id,
        "status": "triggered",
        "severity": alert.get("severity", "unknown"),
        "title": alert.get("title") or alert.get("text") or "Untitled incident",
        "system": alert.get("system", "unknown"),
        "source_alert_id": alert.get("id"),
        "ticket_id": ticket_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "timeline": [
            {
                "timestamp": timestamp,
                "type": "automation",
                "message": "Incident escalation created from high-severity alert.",
            }
        ],
    }

    incident_data.setdefault("incidents", []).append(incident)
    return incident


def process_alerts(dry_run: bool = False) -> None:
    """Process mock alerts and create tickets/incidents for high severity alerts."""
    alert_data = load_alerts()
    ticket_data = load_ticket_data()
    incident_data = load_incidents()

    alerts = alert_data.get("alerts", [])
    high_severity_count = 0
    created_ticket_count = 0
    created_incident_count = 0
    skipped_duplicate_count = 0

    print(f"Found {len(alerts)} alert(s).")

    for alert in alerts:
        alert_id = str(alert.get("id", "unknown"))
        severity = str(alert.get("severity", "unknown")).lower()
        title = alert.get("title") or alert.get("text") or "Untitled alert"

        if not is_high_severity(alert):
            print(f"SKIP: Alert {alert_id} is {severity}, not high severity.")
            logging.info("Skipping non-high-severity alert %s.", alert_id)
            continue

        high_severity_count += 1

        ticket_exists = ticket_already_exists_for_alert(ticket_data, alert_id)
        incident_exists = incident_already_exists_for_alert(incident_data, alert_id)

        if ticket_exists and incident_exists:
            skipped_duplicate_count += 1
            print(f"SKIP: Alert {alert_id} already has ticket and incident records.")
            logging.info("Skipping duplicate alert %s.", alert_id)
            continue

        if dry_run:
            print(f"[DRY RUN] Would create ticket and incident for alert {alert_id}: {title}")
            logging.info("[DRY RUN] Would process alert %s.", alert_id)
            continue

        if not ticket_exists:
            ticket = create_ticket_from_alert(alert, ticket_data)
            created_ticket_count += 1
            print(f"TICKET CREATED: #{ticket['id']} for alert {alert_id}")
            logging.info("Created ticket %s for alert %s.", ticket["id"], alert_id)
        else:
            ticket = next(
                item for item in ticket_data.get("tickets", [])
                if item.get("source_alert_id") == alert_id
            )

        if not incident_exists:
            incident = create_incident_from_alert(alert, incident_data, ticket["id"])
            created_incident_count += 1
            print(f"INCIDENT CREATED: #{incident['id']} for alert {alert_id}")
            logging.info("Created incident %s for alert %s.", incident["id"], alert_id)

    if not dry_run:
        save_ticket_data(ticket_data)
        save_incidents(incident_data)

    print("\nProcessing complete.")
    print(f"High severity alerts found: {high_severity_count}")
    print(f"Tickets created: {created_ticket_count}")
    print(f"Incidents created: {created_incident_count}")
    print(f"Duplicates skipped: {skipped_duplicate_count}")

    logging.info(
        "Processing complete. high=%s tickets=%s incidents=%s duplicates=%s",
        high_severity_count,
        created_ticket_count,
        created_incident_count,
        skipped_duplicate_count,
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Process mock alerts and create tickets/incidents.")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without saving tickets or incidents.",
    )

    return parser.parse_args()


def main() -> None:
    """Run alert handler."""
    args = parse_arguments()
    process_alerts(dry_run=args.dry_run)


if __name__ == "__main__":
    main()