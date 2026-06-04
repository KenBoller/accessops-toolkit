"""
AccessOps Toolkit - New Hire Onboarding
---------------------------------------
Portfolio-safe onboarding automation workflow.

This script:
- Reads mock new hire records from data/new_hires.json
- Validates required employee fields
- Grants access to requested systems through access_management.py
- Creates onboarding tickets in data/tickets.json
- Supports dry-run mode for safe testing

Example usage:
    python tools/new_hire_onboarding.py --dry-run
    python tools/new_hire_onboarding.py
"""

import argparse
import logging
import subprocess
import sys
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

NEW_HIRES_FILE = DATA_DIR / "new_hires.json"
ACCESS_MANAGEMENT_SCRIPT = PROJECT_DIR / "access_management.py"
LOG_FILE = LOG_DIR / "new_hire_onboarding.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.ticket_manager import load_ticket_data, save_ticket_data, now


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


REQUIRED_FIELDS = [
    "employee_id",
    "name",
    "username",
    "department",
    "title",
    "manager",
    "requested_systems",
]


def load_new_hires() -> dict:
    """Load mock new hire records from data/new_hires.json."""
    if not NEW_HIRES_FILE.exists():
        return {"new_hires": []}

    try:
        with NEW_HIRES_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("new_hires.json contains invalid JSON.")
        return {"new_hires": []}


def validate_new_hire_record(new_hire: dict) -> list[str]:
    """Return a list of missing required fields for a new hire record."""
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = new_hire.get(field)

        if value is None or value == "" or value == []:
            missing_fields.append(field)

    return missing_fields


def get_next_ticket_id(ticket_data: dict) -> int:
    """Generate the next mock ticket ID."""
    tickets = ticket_data.get("tickets", [])

    if not tickets:
        return 1001

    return max(int(ticket.get("id", 1000)) for ticket in tickets) + 1


def onboarding_ticket_exists(ticket_data: dict, employee_id: str) -> bool:
    """Prevent duplicate onboarding tickets for the same employee."""
    for ticket in ticket_data.get("tickets", []):
        if ticket.get("source_employee_id") == employee_id and ticket.get("ticket_type") == "onboarding":
            return True

    return False


def create_onboarding_ticket(new_hire: dict, ticket_data: dict, dry_run: bool = False) -> int | None:
    """Create a mock onboarding ticket for a new hire."""
    employee_id = new_hire["employee_id"]

    if onboarding_ticket_exists(ticket_data, employee_id):
        print(f"SKIP: Onboarding ticket already exists for {new_hire['username']}.")
        logging.info("Onboarding ticket already exists for employee %s.", employee_id)
        return None

    ticket_id = get_next_ticket_id(ticket_data)
    timestamp = now()

    title = f"New hire onboarding: {new_hire['name']} ({new_hire['username']})"

    ticket = {
        "id": ticket_id,
        "title": title,
        "status": "open",
        "queue": "onboarding",
        "severity": "normal",
        "ticket_type": "onboarding",
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_to": "automation",
        "system": "accessops",
        "source_employee_id": employee_id,
        "history": [
            {
                "timestamp": timestamp,
                "type": "automation",
                "message": "Onboarding ticket created automatically from new hire record.",
            },
            {
                "timestamp": timestamp,
                "type": "details",
                "message": (
                    f"Name: {new_hire['name']}\n"
                    f"Username: {new_hire['username']}\n"
                    f"Department: {new_hire['department']}\n"
                    f"Title: {new_hire['title']}\n"
                    f"Manager: {new_hire['manager']}\n"
                    f"Requested systems: {', '.join(new_hire['requested_systems'])}"
                ),
            },
        ],
    }

    ticket_data.setdefault("tickets", []).append(ticket)

    if dry_run:
        print(f"[DRY RUN] Would create onboarding ticket #{ticket_id}: {title}")
        logging.info("[DRY RUN] Would create onboarding ticket #%s for %s.", ticket_id, new_hire["username"])
        return ticket_id

    save_ticket_data(ticket_data)

    print(f"TICKET CREATED: #{ticket_id} for {new_hire['username']}")
    logging.info("Created onboarding ticket #%s for %s.", ticket_id, new_hire["username"])

    return ticket_id


def run_access_grant(username: str, system_name: str, dry_run: bool) -> bool:
    """Grant access for one system by calling access_management.py."""
    command = [
        sys.executable,
        str(ACCESS_MANAGEMENT_SCRIPT),
        "grant",
        username,
        "--system",
        system_name,
        "--mock",
    ]

    if not dry_run:
        command.remove("--mock")

    logging.info("Running command: %s", " ".join(command))

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(command)}")
        return True

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(f"ERROR: {result.stderr.strip()}")

    return result.returncode == 0


def grant_requested_access(new_hire: dict, dry_run: bool = False) -> list[str]:
    """Grant all requested systems for a new hire."""
    username = new_hire["username"]
    requested_systems = new_hire.get("requested_systems", [])

    successful_systems = []

    for system_name in requested_systems:
        print(f"Granting {system_name} access for {username}...")

        success = run_access_grant(username, system_name, dry_run)

        if success:
            successful_systems.append(system_name)
            logging.info("Granted %s access to %s.", system_name, username)
        else:
            logging.error("Failed to grant %s access to %s.", system_name, username)

    return successful_systems


def process_new_hire(new_hire: dict, ticket_data: dict, dry_run: bool = False) -> None:
    """Process one new hire record."""
    username = new_hire.get("username", "unknown")
    print(f"\nProcessing new hire: {username}")

    missing_fields = validate_new_hire_record(new_hire)

    if missing_fields:
        print(f"SKIP: {username} is missing required fields: {', '.join(missing_fields)}")
        logging.warning("New hire %s missing fields: %s", username, missing_fields)
        return

    ticket_id = create_onboarding_ticket(new_hire, ticket_data, dry_run=dry_run)

    successful_systems = grant_requested_access(new_hire, dry_run=dry_run)

    if ticket_id and not dry_run:
        add_comment(
            ticket_id,
            f"Access provisioning completed for systems: {', '.join(successful_systems) or 'none'}.",
            comment_type="automation",
        )

    print(f"Completed onboarding workflow for {username}.")
    logging.info("Completed onboarding workflow for %s.", username)


def process_all_new_hires(dry_run: bool = False) -> None:
    """Process all new hires in data/new_hires.json."""
    new_hire_data = load_new_hires()
    new_hires = new_hire_data.get("new_hires", [])
    ticket_data = load_ticket_data()

    print(f"Found {len(new_hires)} new hire record(s).")

    for new_hire in new_hires:
        process_new_hire(new_hire, ticket_data, dry_run=dry_run)

    if not dry_run:
        save_ticket_data(ticket_data)

    print("\nNew hire onboarding processing complete.")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Process mock new hire onboarding records.")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview onboarding actions without changing access or tickets.",
    )

    return parser.parse_args()


def main() -> None:
    """Run new hire onboarding workflow."""
    args = parse_arguments()
    process_all_new_hires(dry_run=args.dry_run)


if __name__ == "__main__":
    main()