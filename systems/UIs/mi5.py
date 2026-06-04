"""
AccessOps Toolkit - MI5 Mock System
-----------------------------------
Portfolio-safe replacement for the old MI5 web-app access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class MI5System(BaseSystem):
    SYSTEM_NAME = "mi5"
    DEFAULT_GROUPS = ["mi5-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_web_app"
    }


if __name__ == "__main__":
    MI5System().run()