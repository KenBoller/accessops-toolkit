"""
AccessOps Toolkit - Alert Ticket Closer
---------------------------------------
Portfolio-safe automation for closing alert tickets after they clear.

This script now uses utils/ticket_manager.py instead of reading/writing
data/tickets.json directly.

Example usage:
    python tools/alert_ticket_closer.py
    python tools/alert_ticket_closer.py --dry-run
"""

import argparse
import logging
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "alert_ticket_closer.log"

LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.ticket_manager import (
    add_comment,
    get_open_tickets,
    resolve_ticket,
)


CLEAR_KEYWORDS = [
    "cleared",
    "alert cleared",
    "resolved",
    "recovered",
    "restored",
    "service recovery",
    "no further action needed",
]


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ticket_has_clear_message(ticket: dict) -> bool:
    """Check whether the ticket history contains a clear/recovery message."""
    for entry in ticket.get("history", []):
        message = entry.get("message", "").lower()

        if any(keyword in message for keyword in CLEAR_KEYWORDS):
            return True

    return False


def close_ticket_if_cleared(ticket: dict, dry_run: bool = False) -> bool:
    """
    Resolve a ticket if clear keywords are found.

    Returns:
        True if the ticket was or would be resolved.
        False if no action was needed.
    """
    ticket_id = ticket.get("id", "unknown")
    title = ticket.get("title", "Untitled ticket")

    if not ticket_has_clear_message(ticket):
        print(f"NO ACTION: Ticket #{ticket_id} has not cleared.")
        logging.info("Ticket #%s has not cleared.", ticket_id)
        return False

    if dry_run:
        print(f"[DRY RUN] Would resolve ticket #{ticket_id}: {title}")
        logging.info("[DRY RUN] Would resolve ticket #%s.", ticket_id)
        return True

    resolution_message = "Ticket automatically resolved after clear condition was detected."

    resolved = resolve_ticket(ticket_id, resolution_message)

    if not resolved:
        print(f"FAILED: Could not resolve ticket #{ticket_id}: {title}")
        logging.error("Failed to resolve ticket #%s.", ticket_id)
        return False

    add_comment(
        ticket_id,
        "Automation confirmed the alert cleared and closed this ticket.",
        comment_type="automation",
    )

    print(f"RESOLVED: Ticket #{ticket_id}: {title}")
    logging.info("Resolved ticket #%s.", ticket_id)

    return True


def process_tickets(dry_run: bool = False) -> None:
    """Process all open alert tickets and close tickets that have cleared."""
    open_tickets = get_open_tickets("alerts")

    print(f"Found {len(open_tickets)} open alert ticket(s).")
    logging.info("Found %s open alert ticket(s).", len(open_tickets))

    resolved_count = 0

    for ticket in open_tickets:
        if close_ticket_if_cleared(ticket, dry_run=dry_run):
            resolved_count += 1

    print(f"Complete. Tickets resolved: {resolved_count}.")
    logging.info("Processing complete. Tickets resolved: %s.", resolved_count)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        description="Auto-close cleared mock alert tickets."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview ticket closures without saving changes.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the alert ticket closer."""
    args = parse_arguments()
    process_tickets(dry_run=args.dry_run)


if __name__ == "__main__":
    main()