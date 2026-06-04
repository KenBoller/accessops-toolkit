"""
AccessOps Toolkit - Engage Mock System
--------------------------------------
Portfolio-safe replacement for the old Engage API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class EngageSystem(BaseSystem):
    SYSTEM_NAME = "engage"
    DEFAULT_GROUPS = ["engage-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_api_app",
        "role": "staff"
    }


if __name__ == "__main__":
    EngageSystem().run()