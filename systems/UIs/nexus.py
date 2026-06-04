"""
AccessOps Toolkit - Nexus Mock System
-------------------------------------
Portfolio-safe replacement for the old Nexus API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class NexusSystem(BaseSystem):
    SYSTEM_NAME = "nexus"
    DEFAULT_GROUPS = ["nexus-dev"]
    DEFAULT_METADATA = {
        "system_type": "artifact_repository",
        "role": "developer"
    }


if __name__ == "__main__":
    NexusSystem().run()