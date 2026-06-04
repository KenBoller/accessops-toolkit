"""
AccessOps Toolkit - Template System Module
------------------------------------------
Copy this file when creating a new mock system integration.

Rename:
    template_system.py -> system_name.py

Update:
    SYSTEM_NAME = "system_name"

Expected usage:
    python system_name.py check kboller
    python system_name.py grant kboller --mock
    python system_name.py remove kboller --mock
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

ACCESS_STATE_FILE = os.path.join(DATA_DIR, "access_state.json")

# Change this when copying the template.
SYSTEM_NAME = "template_system"

LOG_FILE = os.path.join(LOG_DIR, f"{SYSTEM_NAME}.log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_access_state() -> dict:
    """Load mock access records from data/access_state.json."""
    if not os.path.exists(ACCESS_STATE_FILE):
        return {}

    try:
        with open(ACCESS_STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in access_state.json.")
        return {}


def save_access_state(access_state: dict) -> None:
    """Save mock access records to data/access_state.json."""
    with open(ACCESS_STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(access_state, file, indent=2)


def normalize_username(username: str) -> str:
    """Normalize usernames so lookups are consistent."""
    return username.strip().lower()


def check_access(username: str) -> bool:
    """Check whether the target user has access to this system."""
    username = normalize_username(username)
    access_state = load_access_state()

    system_users = access_state.get(SYSTEM_NAME, {})
    user_record = system_users.get(username)

    has_access = bool(user_record and user_record.get("enabled") is True)

    if has_access:
        print(f"ACCESS FOUND: {username} has {SYSTEM_NAME} access.")
        logging.info("Access found for %s in %s.", username, SYSTEM_NAME)
        return True

    print(f"NO ACCESS: {username} does not have {SYSTEM_NAME} access.")
    logging.info("No access found for %s in %s.", username, SYSTEM_NAME)
    return False


def grant_access(username: str, mock_mode: bool) -> None:
    """Grant access to the target user."""
    username = normalize_username(username)

    if mock_mode:
        print(f"[MOCK] Would grant {SYSTEM_NAME} access to {username}.")
        logging.info("[MOCK] Would grant %s access to %s.", SYSTEM_NAME, username)
        return

    access_state = load_access_state()
    access_state.setdefault(SYSTEM_NAME, {})

    access_state[SYSTEM_NAME][username] = {
        "enabled": True,
        "granted_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    save_access_state(access_state)

    print(f"GRANTED: {username} now has {SYSTEM_NAME} access.")
    logging.info("Granted %s access to %s.", SYSTEM_NAME, username)


def remove_access(username: str, mock_mode: bool) -> None:
    """Remove access from the target user."""
    username = normalize_username(username)

    if mock_mode:
        print(f"[MOCK] Would remove {SYSTEM_NAME} access from {username}.")
        logging.info("[MOCK] Would remove %s access from %s.", SYSTEM_NAME, username)
        return

    access_state = load_access_state()
    access_state.setdefault(SYSTEM_NAME, {})

    if username not in access_state[SYSTEM_NAME]:
        print(f"NO CHANGE: {username} did not have {SYSTEM_NAME} access.")
        logging.info("No access to remove for %s in %s.", username, SYSTEM_NAME)
        return

    access_state[SYSTEM_NAME][username]["enabled"] = False
    access_state[SYSTEM_NAME][username]["removed_at"] = datetime.now().isoformat(timespec="seconds")
    access_state[SYSTEM_NAME][username]["updated_at"] = datetime.now().isoformat(timespec="seconds")

    save_access_state(access_state)

    print(f"REMOVED: {username} no longer has {SYSTEM_NAME} access.")
    logging.info("Removed %s access from %s.", SYSTEM_NAME, username)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=f"Manage mock {SYSTEM_NAME} access.")

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
        help="Preview grant/remove actions without changing mock data.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the requested access action."""
    args = parse_arguments()

    if args.action == "check":
        has_access = check_access(args.username)
        sys.exit(0 if has_access else 1)

    if args.action == "grant":
        grant_access(args.username, args.mock)
        sys.exit(0)

    if args.action == "remove":
        remove_access(args.username, args.mock)
        sys.exit(0)


if __name__ == "__main__":
    main()