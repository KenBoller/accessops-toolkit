"""
AccessOps Toolkit - Microsites Mock System
------------------------------------------
Portfolio-safe replacement for the old Microsites DB-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class MicrositesSystem(BaseSystem):
    SYSTEM_NAME = "microsites"
    DEFAULT_GROUPS = ["microsites-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_mysql_app"
    }


if __name__ == "__main__":
    MicrositesSystem().run()