"""
AccessOps Toolkit - Outage Manager
----------------------------------
Portfolio-safe major incident workflow.

This script:
- Creates an outage ticket
- Creates/links a triggered incident
- Creates a mock bridge call record
- Creates a mock team notification
- Supports dry-run mode

Example usage:
    python tools/outage_manager.py "Major API outage affecting production" --severity critical --dry-run
    python tools/outage_manager.py "Database outage affecting customers" --severity sev1
"""

import argparse
import json
import logging
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

INCIDENTS_FILE = DATA_DIR / "incidents.json"
BRIDGES_FILE = DATA_DIR / "bridges.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
LOG_FILE = LOG_DIR / "outage_manager.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.ticket_manager import load_ticket_data, save_ticket_data, now


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


VALID_SEVERITIES = {"critical", "major", "sev0", "sev1", "sev2"}


def load_json_file(path: Path, default: dict) -> dict:
    """Load JSON data from a file."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in %s.", path)
        return default


def save_json_file(path: Path, data: dict) -> None:
    """Save JSON data to a file."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_incidents() -> dict:
    """Load incident records."""
    return load_json_file(INCIDENTS_FILE, {"incidents": []})


def save_incidents(data: dict) -> None:
    """Save incident records."""
    save_json_file(INCIDENTS_FILE, data)


def load_bridges() -> dict:
    """Load bridge call records."""
    return load_json_file(BRIDGES_FILE, {"bridges": []})


def save_bridges(data: dict) -> None:
    """Save bridge call records."""
    save_json_file(BRIDGES_FILE, data)


def load_notifications() -> dict:
    """Load notification records."""
    return load_json_file(NOTIFICATIONS_FILE, {"notifications": []})


def save_notifications(data: dict) -> None:
    """Save notification records."""
    save_json_file(NOTIFICATIONS_FILE, data)


def get_next_id(records: list[dict], default_start: int) -> int:
    """Generate the next numeric ID for a list of records."""
    if not records:
        return default_start

    return max(int(record.get("id", default_start - 1)) for record in records) + 1


def get_next_ticket_id(ticket_data: dict) -> int:
    """Generate the next ticket ID."""
    return get_next_id(ticket_data.get("tickets", []), 1001)


def create_outage_ticket(description: str, severity: str, dry_run: bool = False) -> dict:
    """Create a mock outage ticket."""
    ticket_data = load_ticket_data()
    ticket_id = get_next_ticket_id(ticket_data)
    timestamp = now()

    ticket = {
        "id": ticket_id,
        "title": f"Outage: {description}",
        "status": "open",
        "queue": "incidents",
        "severity": severity,
        "ticket_type": "outage",
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_to": "incident_commander",
        "system": "accessops",
        "history": [
            {
                "timestamp": timestamp,
                "type": "outage",
                "message": f"Major outage workflow started: {description}",
            }
        ],
    }

    if dry_run:
        print(f"[DRY RUN] Would create outage ticket #{ticket_id}: {description}")
        logging.info("[DRY RUN] Would create outage ticket #%s.", ticket_id)
        return ticket

    ticket_data.setdefault("tickets", []).append(ticket)
    save_ticket_data(ticket_data)

    print(f"TICKET CREATED: #{ticket_id} for outage.")
    logging.info("Created outage ticket #%s.", ticket_id)

    return ticket


def create_incident(description: str, severity: str, ticket_id: int, dry_run: bool = False) -> dict:
    """Create a mock major incident record."""
    incident_data = load_incidents()
    incident_id = get_next_id(incident_data.get("incidents", []), 5001)
    timestamp = now()

    incident = {
        "id": incident_id,
        "status": "triggered",
        "severity": severity,
        "title": description,
        "system": "accessops",
        "ticket_id": ticket_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "timeline": [
            {
                "timestamp": timestamp,
                "type": "outage",
                "message": "Major incident created from outage manager workflow.",
            }
        ],
    }

    if dry_run:
        print(f"[DRY RUN] Would create incident #{incident_id}.")
        logging.info("[DRY RUN] Would create incident #%s.", incident_id)
        return incident

    incident_data.setdefault("incidents", []).append(incident)
    save_incidents(incident_data)

    print(f"INCIDENT CREATED: #{incident_id}")
    logging.info("Created incident #%s.", incident_id)

    return incident


def create_bridge_call(incident_id: int, dry_run: bool = False) -> dict:
    """Create a mock bridge call record."""
    bridge_data = load_bridges()
    bridge_id = get_next_id(bridge_data.get("bridges", []), 7001)
    timestamp = now()

    bridge = {
        "id": bridge_id,
        "incident_id": incident_id,
        "status": "open",
        "bridge_url": f"https://bridge.example.com/{bridge_id}",
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    if dry_run:
        print(f"[DRY RUN] Would open bridge call #{bridge_id}.")
        logging.info("[DRY RUN] Would open bridge call #%s.", bridge_id)
        return bridge

    bridge_data.setdefault("bridges", []).append(bridge)
    save_bridges(bridge_data)

    print(f"BRIDGE OPENED: {bridge['bridge_url']}")
    logging.info("Opened bridge call #%s.", bridge_id)

    return bridge


def create_notification(description: str, severity: str, ticket_id: int, incident_id: int, bridge_url: str, dry_run: bool = False) -> dict:
    """Create a mock team notification record."""
    notification_data = load_notifications()
    notification_id = get_next_id(notification_data.get("notifications", []), 9001)
    timestamp = now()

    notification = {
        "id": notification_id,
        "channel": "ops-alerts",
        "severity": severity,
        "message": (
            f"Outage declared: {description} | "
            f"Ticket #{ticket_id} | Incident #{incident_id} | Bridge: {bridge_url}"
        ),
        "created_at": timestamp,
    }

    if dry_run:
        print(f"[DRY RUN] Would notify ops-alerts channel.")
        logging.info("[DRY RUN] Would create notification #%s.", notification_id)
        return notification

    notification_data.setdefault("notifications", []).append(notification)
    save_notifications(notification_data)

    print(f"NOTIFICATION CREATED: #{notification_id}")
    logging.info("Created notification #%s.", notification_id)

    return notification


def handle_outage(description: str, severity: str, dry_run: bool = False) -> None:
    """Run the full outage workflow."""
    severity = severity.lower()

    if severity not in VALID_SEVERITIES:
        print(f"Invalid severity: {severity}")
        print(f"Valid severities: {', '.join(sorted(VALID_SEVERITIES))}")
        return

    print(f"Handling outage: {description}")
    print(f"Severity: {severity}")

    ticket = create_outage_ticket(description, severity, dry_run=dry_run)
    incident = create_incident(description, severity, ticket["id"], dry_run=dry_run)
    bridge = create_bridge_call(incident["id"], dry_run=dry_run)
    create_notification(
        description=description,
        severity=severity,
        ticket_id=ticket["id"],
        incident_id=incident["id"],
        bridge_url=bridge["bridge_url"],
        dry_run=dry_run,
    )

    print("\nOutage workflow complete.")
    print(f"Ticket: #{ticket['id']}")
    print(f"Incident: #{incident['id']}")
    print(f"Bridge: {bridge['bridge_url']}")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run a mock major outage workflow.")

    parser.add_argument(
        "description",
        help="Short outage description.",
    )

    parser.add_argument(
        "--severity",
        default="critical",
        help="Outage severity. Example: critical, major, sev0, sev1, sev2.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the outage workflow without saving records.",
    )

    return parser.parse_args()


def main() -> None:
    """Run outage manager."""
    args = parse_arguments()
    handle_outage(args.description, args.severity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()