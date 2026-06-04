"""
AccessOps Toolkit - Base System Module
--------------------------------------
Shared base class for all mock system integrations.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))

from utils.access_state import load_access_state, save_access_state, normalize_username


class BaseSystem:
    """Base class for a mock access-managed system."""

    SYSTEM_NAME = "base_system"
    DEFAULT_GROUPS: list[str] = []
    DEFAULT_METADATA: dict = {}

    def __init__(self) -> None:
        self.log_file = LOG_DIR / f"{self.SYSTEM_NAME}.log"
        self.configure_logging()

    def configure_logging(self) -> None:
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def get_system_users(self, access_state: dict) -> dict:
        access_state.setdefault(self.SYSTEM_NAME, {})
        return access_state[self.SYSTEM_NAME]

    def check_access(self, username: str) -> bool:
        username = normalize_username(username)
        access_state = load_access_state()

        system_users = access_state.get(self.SYSTEM_NAME, {})
        user_record = system_users.get(username)

        has_access = bool(user_record and user_record.get("enabled") is True)

        if has_access:
            print(f"ACCESS FOUND: {username} has {self.SYSTEM_NAME} access.")
            logging.info("Access found for %s in %s.", username, self.SYSTEM_NAME)
            return True

        print(f"NO ACCESS: {username} does not have {self.SYSTEM_NAME} access.")
        logging.info("No access found for %s in %s.", username, self.SYSTEM_NAME)
        return False

    def build_grant_record(self) -> dict:
        timestamp = self.now()

        record = {
            "enabled": True,
            "granted_at": timestamp,
            "updated_at": timestamp,
        }

        if self.DEFAULT_GROUPS:
            record["groups"] = self.DEFAULT_GROUPS

        if self.DEFAULT_METADATA:
            record.update(self.DEFAULT_METADATA)

        return record

    def grant_access(self, username: str, mock_mode: bool = False, dry_run: bool = False) -> None:
        username = normalize_username(username)

        if dry_run:
            print(f"[DRY RUN] Would grant {self.SYSTEM_NAME} access to {username}.")
            logging.info("[DRY RUN] Would grant %s access to %s.", self.SYSTEM_NAME, username)
            return

        access_state = load_access_state()
        system_users = self.get_system_users(access_state)

        system_users[username] = self.build_grant_record()
        save_access_state(access_state)

        if mock_mode:
            print(f"[MOCK] GRANTED: {username} now has {self.SYSTEM_NAME} access.")
        else:
            print(f"GRANTED: {username} now has {self.SYSTEM_NAME} access.")

        logging.info("Granted %s access to %s.", self.SYSTEM_NAME, username)

    def remove_access(self, username: str, mock_mode: bool = False, dry_run: bool = False) -> None:
        username = normalize_username(username)

        if dry_run:
            print(f"[DRY RUN] Would remove {self.SYSTEM_NAME} access from {username}.")
            logging.info("[DRY RUN] Would remove %s access from %s.", self.SYSTEM_NAME, username)
            return

        access_state = load_access_state()
        system_users = self.get_system_users(access_state)

        if username not in system_users:
            print(f"NO CHANGE: {username} did not have {self.SYSTEM_NAME} access.")
            logging.info("No access to remove for %s in %s.", username, self.SYSTEM_NAME)
            return

        timestamp = self.now()
        system_users[username]["enabled"] = False
        system_users[username]["removed_at"] = timestamp
        system_users[username]["updated_at"] = timestamp

        save_access_state(access_state)

        if mock_mode:
            print(f"[MOCK] REMOVED: {username} no longer has {self.SYSTEM_NAME} access.")
        else:
            print(f"REMOVED: {username} no longer has {self.SYSTEM_NAME} access.")

        logging.info("Removed %s access from %s.", self.SYSTEM_NAME, username)

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description=f"Manage mock {self.SYSTEM_NAME} access."
        )

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
            help="Preview grant/remove actions without changing mock data.",
        )

        return parser.parse_args()

    def run(self) -> None:
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