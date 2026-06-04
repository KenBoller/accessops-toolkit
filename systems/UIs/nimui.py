"""
AccessOps Toolkit - NimUI Mock System
-------------------------------------
Portfolio-safe replacement for the old NimUI Oracle-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class NimUISystem(BaseSystem):
    SYSTEM_NAME = "nimui"
    DEFAULT_GROUPS = ["nimui-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_oracle_app"
    }


if __name__ == "__main__":
    NimUISystem().run()