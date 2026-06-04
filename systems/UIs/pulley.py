"""
AccessOps Toolkit - Pulley Mock System
--------------------------------------
Portfolio-safe replacement for the old Pulley API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class PulleySystem(BaseSystem):
    SYSTEM_NAME = "pulley"
    DEFAULT_GROUPS = ["pulley-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_api_app",
        "role": "standard"
    }


if __name__ == "__main__":
    PulleySystem().run()