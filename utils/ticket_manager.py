"""
AccessOps Toolkit - Mock Ticket API
-----------------------------------
Portfolio-safe replacement for the old RT API helper.

This module reads and writes local mock ticket data from:

    data/tickets.json

It provides ticket-style helper functions that other scripts can use without
knowing how the ticket data is stored.
"""

import json
import logging
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

TICKETS_FILE = DATA_DIR / "tickets.json"
LOG_FILE = LOG_DIR / "ticket_manager.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def now() -> str:
    """Return a consistent timestamp string."""
    return datetime.now().isoformat(timespec="seconds")


def load_ticket_data() -> dict:
    """Load ticket data from data/tickets.json."""
    if not TICKETS_FILE.exists():
        return {"tickets": []}

    try:
        with TICKETS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("tickets.json contains invalid JSON.")
        return {"tickets": []}


def save_ticket_data(ticket_data: dict) -> None:
    """Save ticket data to data/tickets.json."""
    with TICKETS_FILE.open("w", encoding="utf-8") as file:
        json.dump(ticket_data, file, indent=2)


def get_all_tickets() -> list[dict]:
    """Return all tickets."""
    return load_ticket_data().get("tickets", [])


def get_ticket_details(ticket_id: int | str) -> dict | None:
    """Return one ticket by ID."""
    ticket_id = str(ticket_id)

    for ticket in get_all_tickets():
        if str(ticket.get("id")) == ticket_id:
            return ticket

    logging.warning("Ticket not found: %s", ticket_id)
    return None


def get_open_tickets(queue_name: str | None = None) -> list[dict]:
    """
    Return open tickets.

    Args:
        queue_name: Optional queue filter, such as "alerts".
    """
    tickets = get_all_tickets()

    open_tickets = [
        ticket
        for ticket in tickets
        if ticket.get("status") == "open"
    ]

    if queue_name:
        open_tickets = [
            ticket
            for ticket in open_tickets
            if ticket.get("queue") == queue_name
        ]

    logging.info("Found %s open ticket(s).", len(open_tickets))
    return open_tickets


def get_latest_ticket_comment(ticket_id: int | str) -> str | None:
    """Return the latest history message from a ticket."""
    ticket = get_ticket_details(ticket_id)

    if not ticket:
        return None

    history = ticket.get("history", [])

    if not history:
        return None

    return history[-1].get("message")


def add_comment(ticket_id: int | str, comment: str, comment_type: str = "comment") -> bool:
    """
    Add a history entry/comment to a ticket.

    Returns True if the comment was added.
    """
    if not comment or not comment.strip():
        logging.warning("Skipping empty comment for ticket %s.", ticket_id)
        return False

    ticket_data = load_ticket_data()
    ticket = None

    for item in ticket_data.get("tickets", []):
        if str(item.get("id")) == str(ticket_id):
            ticket = item
            break

    if not ticket:
        logging.warning("Cannot comment. Ticket not found: %s", ticket_id)
        return False

    timestamp = now()

    ticket.setdefault("history", []).append(
        {
            "timestamp": timestamp,
            "type": comment_type,
            "message": comment.strip(),
        }
    )

    ticket["updated_at"] = timestamp

    save_ticket_data(ticket_data)

    logging.info("Added comment to ticket %s.", ticket_id)
    return True


def resolve_ticket(ticket_id: int | str, resolution_message: str | None = None) -> bool:
    """
    Resolve a ticket and optionally append a resolution comment.
    """
    ticket_data = load_ticket_data()
    ticket = None

    for item in ticket_data.get("tickets", []):
        if str(item.get("id")) == str(ticket_id):
            ticket = item
            break

    if not ticket:
        logging.warning("Cannot resolve. Ticket not found: %s", ticket_id)
        return False

    timestamp = now()

    ticket["status"] = "resolved"
    ticket["updated_at"] = timestamp

    ticket.setdefault("history", []).append(
        {
            "timestamp": timestamp,
            "type": "resolution",
            "message": resolution_message or "Ticket resolved by automation.",
        }
    )

    save_ticket_data(ticket_data)

    logging.info("Resolved ticket %s.", ticket_id)
    return True


def reopen_ticket(ticket_id: int | str, reason: str | None = None) -> bool:
    """
    Reopen a resolved ticket.
    Useful for future testing or workflow simulation.
    """
    ticket_data = load_ticket_data()
    ticket = None

    for item in ticket_data.get("tickets", []):
        if str(item.get("id")) == str(ticket_id):
            ticket = item
            break

    if not ticket:
        logging.warning("Cannot reopen. Ticket not found: %s", ticket_id)
        return False

    timestamp = now()

    ticket["status"] = "open"
    ticket["updated_at"] = timestamp

    ticket.setdefault("history", []).append(
        {
            "timestamp": timestamp,
            "type": "reopen",
            "message": reason or "Ticket reopened.",
        }
    )

    save_ticket_data(ticket_data)

    logging.info("Reopened ticket %s.", ticket_id)
    return True


if __name__ == "__main__":
    print("Open alert tickets:")
    for ticket in get_open_tickets("alerts"):
        print(f"#{ticket.get('id')} - {ticket.get('title')}")