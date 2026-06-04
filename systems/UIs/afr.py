"""
AccessOps Toolkit - AFR Mock System
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class AFRSystem(BaseSystem):
    SYSTEM_NAME = "afr"
    DEFAULT_GROUPS = ["afr-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_oracle_app"
    }


if __name__ == "__main__":
    AFRSystem().run()