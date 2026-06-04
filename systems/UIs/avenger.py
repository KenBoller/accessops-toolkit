"""
AccessOps Toolkit - Avenger Mock System
---------------------------------------
Portfolio-safe replacement for the old MySQL-backed Avenger access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class AvengerSystem(BaseSystem):
    SYSTEM_NAME = "avenger"
    DEFAULT_GROUPS = ["avenger-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_mysql_app"
    }


if __name__ == "__main__":
    AvengerSystem().run()