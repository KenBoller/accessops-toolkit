"""
AccessOps Toolkit - Ticketing Mock System
-----------------------------------------
Portfolio-safe ticketing access module.
"""

import argparse
import logging
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "ticketing.log"

LOG_DIR.mkdir(exist_ok=True)

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem
from utils.access_state import normalize_username
from utils.ticket_manager import load_ticket_data, save_ticket_data, now


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class TicketingSystem(BaseSystem):
    """Mock ticketing system access module."""

    SYSTEM_NAME = "ticketing"
    DEFAULT_GROUPS = ["ticket-user"]

    def get_owned_open_tickets(self, username: str) -> list[dict]:
        """Return open tickets currently assigned to the user."""
        username = normalize_username(username)
        ticket_data = load_ticket_data()

        return [
            ticket
            for ticket in ticket_data.get("tickets", [])
            if ticket.get("status") == "open"
            and normalize_username(str(ticket.get("assigned_to", ""))) == username
        ]

    def reassign_owned_tickets(self, username: str, dry_run: bool = False) -> int:
        """Reassign open tickets owned by the user to automation."""
        username = normalize_username(username)
        ticket_data = load_ticket_data()
        reassigned_count = 0
        timestamp = now()

        for ticket in ticket_data.get("tickets", []):
            assigned_to = normalize_username(str(ticket.get("assigned_to", "")))

            if ticket.get("status") == "open" and assigned_to == username:
                reassigned_count += 1
                ticket_id = ticket.get("id", "unknown")

                if dry_run:
                    print(f"[DRY RUN] Would reassign ticket #{ticket_id} from {username} to automation.")
                    logging.info("[DRY RUN] Would reassign ticket #%s from %s.", ticket_id, username)
                    continue

                ticket["assigned_to"] = "automation"
                ticket["updated_at"] = timestamp
                ticket.setdefault("history", []).append(
                    {
                        "timestamp": timestamp,
                        "type": "automation",
                        "message": f"Ticket reassigned from {username} to automation before access removal.",
                    }
                )

                print(f"REASSIGNED: Ticket #{ticket_id} from {username} to automation.")
                logging.info("Reassigned ticket #%s from %s.", ticket_id, username)

        if not dry_run:
            save_ticket_data(ticket_data)

        return reassigned_count

    def check_access(self, username: str) -> bool:
        """Check ticketing access and report open tickets owned by the user."""
        has_access = super().check_access(username)

        username = normalize_username(username)
        owned_tickets = self.get_owned_open_tickets(username)

        if owned_tickets:
            print(f"OPEN TICKETS: {username} owns {len(owned_tickets)} open ticket(s).")
            for ticket in owned_tickets:
                print(f"  - #{ticket.get('id')}: {ticket.get('title')}")
        else:
            print(f"OPEN TICKETS: {username} owns 0 open ticket(s).")

        return has_access

    def remove_access(
        self,
        username: str,
        mock_mode: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Remove ticketing access after reassigning owned open tickets."""
        username = normalize_username(username)
        owned_tickets = self.get_owned_open_tickets(username)

        if owned_tickets:
            print(f"PRE-CHECK: {username} owns {len(owned_tickets)} open ticket(s).")
            self.reassign_owned_tickets(username, dry_run=dry_run)
        else:
            print(f"PRE-CHECK: {username} owns no open tickets.")

        super().remove_access(username, mock_mode=mock_mode, dry_run=dry_run)

    def parse_arguments(self) -> argparse.Namespace:
        """Parse standard system-module CLI arguments."""
        parser = argparse.ArgumentParser(description="Manage mock ticketing access.")

        parser.add_argument(
            "action",
            choices=["check", "grant", "remove"],
            help="Access action to perform.",
        )

        parser.add_argument(
            "username",
            help="Target username.",
        )

        parser.add_argument(
            "--mock",
            action="store_true",
            help="Run in portfolio-safe mock mode while still updating local mock state.",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving.",
        )

        return parser.parse_args()

    def run(self) -> None:
        """Run the requested access action."""
        args = self.parse_arguments()

        if args.action == "check":
            has_access = self.check_access(args.username)
            sys.exit(0 if has_access else 1)

        if args.action == "grant":
            self.grant_access(args.username, mock_mode=args.mock, dry_run=args.dry_run)
            sys.exit(0)

        if args.action == "remove":
            self.remove_access(args.username, mock_mode=args.mock, dry_run=args.dry_run)
            sys.exit(0)


if __name__ == "__main__":
    TicketingSystem().run()