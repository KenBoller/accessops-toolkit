"""
Generic secret loader for the SOC access portfolio project.

Looks for a JSON credentials file using SOC_SECRET_FILE first, then falls
back to ./config/creds.example.json. Never commit real secrets.
"""

import json
import logging
import os
from pathlib import Path

DEFAULT_SECRET_FILE = Path(__file__).resolve().parents[1] / "config" / "creds.example.json"
SECRETS_FILE = Path(os.environ.get("SOC_SECRET_FILE", DEFAULT_SECRET_FILE)).expanduser()


def get_secret(key: str, default=None):
    """Return one secret value from the configured JSON file."""
    try:
        with SECRETS_FILE.open("r", encoding="utf-8") as file:
            secrets = json.load(file)
        return secrets.get(key, default)
    except FileNotFoundError:
        logging.error("Secrets file not found: %s", SECRETS_FILE)
    except json.JSONDecodeError:
        logging.error("Secrets file is not valid JSON: %s", SECRETS_FILE)
    except Exception as error:
        logging.error("Error loading secret %s: %s", key, error)
    return default