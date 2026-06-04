"""
AccessOps Toolkit - Auth Validator
----------------------------------
Portfolio-safe mock authentication validator.

This replaces old LDAP test scripts with a safe local demo auth workflow.

This script:
- Reads mock operator accounts from data/operators.json
- Validates username/password combinations
- Supports checking whether an operator is active
- Supports role display for demo purposes
- Does NOT connect to LDAP, AD, SSO, or any real identity provider

Example usage:
    python tools/auth_validator.py kboller password123
    python tools/auth_validator.py admin password123
    python tools/auth_validator.py --list-users
"""

import argparse
import json
import logging
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
LOG_DIR = PROJECT_DIR / "logs"

OPERATORS_FILE = DATA_DIR / "operators.json"
LOG_FILE = LOG_DIR / "auth_validator.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_operators() -> dict:
    """Load mock operator accounts from data/operators.json."""
    if not OPERATORS_FILE.exists():
        return {"operators": []}

    try:
        with OPERATORS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("operators.json contains invalid JSON.")
        return {"operators": []}


def normalize_username(username: str) -> str:
    """Normalize usernames for consistent lookup."""
    return username.strip().lower()


def find_operator(username: str) -> dict | None:
    """Find one operator account by username."""
    username = normalize_username(username)
    operator_data = load_operators()

    for operator in operator_data.get("operators", []):
        if normalize_username(operator.get("username", "")) == username:
            return operator

    return None


def validate_operator(username: str, password: str) -> bool:
    """
    Validate a mock operator username/password.

    This is intentionally simple for portfolio/demo use.
    Do not use this pattern for production authentication.
    """
    operator = find_operator(username)

    if not operator:
        print(f"AUTH FAILED: Operator '{username}' was not found.")
        logging.warning("Authentication failed. Operator not found: %s", username)
        return False

    if not operator.get("active", False):
        print(f"AUTH FAILED: Operator '{username}' is inactive.")
        logging.warning("Authentication failed. Operator inactive: %s", username)
        return False

    expected_password = operator.get("password")

    if password != expected_password:
        print(f"AUTH FAILED: Invalid password for '{username}'.")
        logging.warning("Authentication failed. Invalid password for: %s", username)
        return False

    roles = ", ".join(operator.get("roles", [])) or "no roles"

    print(f"AUTH SUCCESS: {username} authenticated.")
    print(f"Roles: {roles}")

    logging.info("Authentication successful for operator: %s", username)
    return True


def list_users() -> None:
    """Print configured mock operator accounts."""
    operator_data = load_operators()
    operators = operator_data.get("operators", [])

    if not operators:
        print("No operators found.")
        return

    print("Configured operators:")
    for operator in operators:
        username = operator.get("username", "unknown")
        active = operator.get("active", False)
        roles = ", ".join(operator.get("roles", [])) or "no roles"
        status = "active" if active else "inactive"

        print(f"  - {username} ({status}) [{roles}]")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate mock operator credentials.")

    parser.add_argument(
        "username",
        nargs="?",
        help="Operator username.",
    )

    parser.add_argument(
        "password",
        nargs="?",
        help="Operator password.",
    )

    parser.add_argument(
        "--list-users",
        action="store_true",
        help="List configured mock operator accounts.",
    )

    return parser.parse_args()


def main() -> None:
    """Run auth validation."""
    args = parse_arguments()

    if args.list_users:
        list_users()
        return

    if not args.username or not args.password:
        print("Username and password are required unless using --list-users.")
        print("Example: python tools/auth_validator.py admin password123")
        return

    validate_operator(args.username, args.password)


if __name__ == "__main__":
    main()