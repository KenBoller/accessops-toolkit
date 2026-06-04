"""
AccessOps Toolkit - User Access Request Processor
-------------------------------------------------
Portfolio-safe workflow for processing access requests.

This script:
- Reads mock access requests from data/access_requests.json
- Grants access automatically for SOC-managed systems
- Creates approval tickets for restricted access
- Skips duplicate approval tickets
- Supports dry-run mode

Example usage:
    python tools/user_access_requests.py --dry-run
    python tools/user_access_requests.py
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

ACCESS_REQUESTS_FILE = DATA_DIR / "access_requests.json"
ACCESS_MANAGEMENT_SCRIPT = PROJECT_DIR / "access_management.py"
LOG_FILE = LOG_DIR / "user_access_requests.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.ticket_manager import load_ticket_data, save_ticket_data, now
from utils.id_generator import get_next_id


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


AUTO_APPROVED_SYSTEMS = {
    "jira",
    "adtrack",
    "ticketing",
}

REQUIRES_APPROVAL = {
    "production_db_write": "Database Admin Team",
    "production_sudo": "Platform Engineering",
    "billing_admin": "Finance Systems Owner",
    "auth_admin": "Identity Admin",
}


def load_access_requests() -> dict:
    """Load mock access requests from data/access_requests.json."""
    if not ACCESS_REQUESTS_FILE.exists():
        return {"access_requests": []}

    try:
        with ACCESS_REQUESTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("access_requests.json contains invalid JSON.")
        return {"access_requests": []}


def save_access_requests(access_request_data: dict) -> None:
    """Save access requests back to data/access_requests.json."""
    with ACCESS_REQUESTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(access_request_data, file, indent=2)


def normalize_system_name(system_name: str) -> str:
    """Normalize system names for comparison."""
    return system_name.strip().lower().replace(" ", "_").replace("-", "_")


def approval_ticket_exists(ticket_data: dict, request_id: str) -> bool:
    """Prevent duplicate approval tickets for the same request."""
    for ticket in ticket_data.get("tickets", []):
        if ticket.get("source_request_id") == request_id and ticket.get("ticket_type") == "approval":
            return True

    return False


def mark_request_status(request: dict, status: str, note: str | None = None) -> None:
    """Update an access request status."""
    request["status"] = status
    request["updated_at"] = now()

    if note:
        request.setdefault("history", []).append(
            {
                "timestamp": now(),
                "type": "automation",
                "message": note,
            }
        )


def run_access_grant(username: str, system_name: str, dry_run: bool) -> bool:
    """Grant access by calling access_management.py."""
    command = [
        sys.executable,
        str(ACCESS_MANAGEMENT_SCRIPT),
        "grant",
        username,
        "--system",
        system_name,
    ]

    if dry_run:
        command.append("--mock")

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


def create_approval_ticket(request: dict, approver: str, ticket_data: dict, dry_run: bool = False) -> int | None:
    """Create a mock approval ticket for restricted access."""
    request_id = request["request_id"]

    if approval_ticket_exists(ticket_data, request_id):
        print(f"SKIP: Approval ticket already exists for request {request_id}.")
        logging.info("Approval ticket already exists for request %s.", request_id)
        return None

    ticket_id = get_next_id(ticket_data.get("tickets", []), 1001)
    timestamp = now()

    requested_system = request["requested_system"]
    username = request["username"]

    ticket = {
        "id": ticket_id,
        "title": f"Approval required: {requested_system} for {username}",
        "status": "open",
        "queue": "approvals",
        "severity": "normal",
        "ticket_type": "approval",
        "created_at": timestamp,
        "updated_at": timestamp,
        "assigned_to": approver,
        "system": "accessops",
        "source_request_id": request_id,
        "history": [
            {
                "timestamp": timestamp,
                "type": "approval",
                "message": (
                    f"Access request {request_id} requires approval from {approver}.\n"
                    f"User: {username}\n"
                    f"Requested system: {requested_system}\n"
                    f"Reason: {request.get('reason', 'No reason provided')}"
                ),
            }
        ],
    }

    ticket_data.setdefault("tickets", []).append(ticket)

    if dry_run:
        print(f"[DRY RUN] Would create approval ticket #{ticket_id} for request {request_id}.")
        logging.info("[DRY RUN] Would create approval ticket #%s for request %s.", ticket_id, request_id)
        return ticket_id

    save_ticket_data(ticket_data)

    print(f"APPROVAL TICKET CREATED: #{ticket_id} for request {request_id}")
    logging.info("Created approval ticket #%s for request %s.", ticket_id, request_id)

    return ticket_id


def process_access_request(request: dict, ticket_data: dict, dry_run: bool = False) -> None:
    """Process one access request."""
    request_id = request.get("request_id", "unknown")
    username = request.get("username", "")
    requested_system_raw = request.get("requested_system", "")
    requested_system = normalize_system_name(requested_system_raw)

    print(f"\nProcessing request {request_id}: {username} -> {requested_system_raw}")

    if not username or not requested_system:
        print(f"SKIP: Request {request_id} is missing username or requested_system.")
        mark_request_status(request, "invalid", "Missing username or requested system.")
        return

    current_status = request.get("status", "new")

    if current_status not in {"new", "pending"}:
        print(f"SKIP: Request {request_id} already has status '{current_status}'.")
        return

    if requested_system in AUTO_APPROVED_SYSTEMS:
        print(f"AUTO-APPROVED: {requested_system_raw} is managed by AccessOps.")

        success = run_access_grant(username, requested_system, dry_run)

        if success:
            mark_request_status(
                request,
                "completed" if not dry_run else "would_complete",
                f"Access granted for {requested_system}.",
            )
            print(f"COMPLETED: {request_id} for {username}.")
        else:
            mark_request_status(
                request,
                "failed",
                f"Failed to grant access for {requested_system}.",
            )
            print(f"FAILED: Could not grant {requested_system} access for {username}.")

    elif requested_system in REQUIRES_APPROVAL:
        approver = REQUIRES_APPROVAL[requested_system]
        print(f"APPROVAL REQUIRED: {requested_system_raw} requires approval from {approver}.")

        ticket_id = create_approval_ticket(request, approver, ticket_data, dry_run=dry_run)

        mark_request_status(
            request,
            "pending_approval" if not dry_run else "would_require_approval",
            f"Approval ticket {'would be created' if dry_run else 'created'} for {requested_system}.",
        )

        if ticket_id:
            print(f"PENDING APPROVAL: Request {request_id} linked to ticket #{ticket_id}.")

    else:
        print(f"UNMANAGED: {requested_system_raw} is not managed by AccessOps.")
        mark_request_status(
            request,
            "manual_review",
            f"Requested system {requested_system_raw} is not managed by automation.",
        )


def process_all_requests(dry_run: bool = False) -> None:
    """Process all access requests."""
    access_request_data = load_access_requests()
    ticket_data = load_ticket_data()

    requests = access_request_data.get("access_requests", [])

    print(f"Found {len(requests)} access request(s).")

    for request in requests:
        process_access_request(request, ticket_data, dry_run=dry_run)

    if not dry_run:
        save_access_requests(access_request_data)
        save_ticket_data(ticket_data)

    print("\nAccess request processing complete.")


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Process mock user access requests.")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview request processing without saving changes.",
    )

    return parser.parse_args()


def main() -> None:
    """Run access request processor."""
    args = parse_arguments()
    process_all_requests(dry_run=args.dry_run)


if __name__ == "__main__":
    main()