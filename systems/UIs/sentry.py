"""
AccessOps Toolkit - Sentry Mock System
--------------------------------------
Portfolio-safe replacement for the old Sentry API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class SentrySystem(BaseSystem):
    SYSTEM_NAME = "sentry"
    DEFAULT_GROUPS = ["sentry-member"]
    DEFAULT_METADATA = {
        "system_type": "error_monitoring",
        "role": "member"
    }


if __name__ == "__main__":
    SentrySystem().run()