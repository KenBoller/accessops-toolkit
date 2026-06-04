import json
import logging
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"

ACCESS_STATE_FILE = DATA_DIR / "access_state.json"


def load_access_state() -> dict:
    """Load access state JSON."""
    if not ACCESS_STATE_FILE.exists():
        return {}

    try:
        with ACCESS_STATE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Invalid JSON in access_state.json")
        return {}


def save_access_state(access_state: dict) -> None:
    """Save access state JSON."""
    with ACCESS_STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(access_state, file, indent=2)


def normalize_username(username: str) -> str:
    """Normalize usernames for consistency."""
    return username.strip().lower()