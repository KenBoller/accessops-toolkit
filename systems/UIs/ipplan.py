"""
AccessOps Toolkit - IPPlan Mock System
--------------------------------------
Portfolio-safe replacement for the old IPPlan access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class IPPlanSystem(BaseSystem):
    SYSTEM_NAME = "ipplan"
    DEFAULT_GROUPS = ["ipplan-user"]
    DEFAULT_METADATA = {
        "system_type": "network_management"
    }


if __name__ == "__main__":
    IPPlanSystem().run()