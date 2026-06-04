"""
AccessOps Toolkit - PagerDuty Mock System
-----------------------------------------
Portfolio-safe replacement for the old PagerDuty API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class PagerDutySystem(BaseSystem):
    SYSTEM_NAME = "pagerduty"
    DEFAULT_GROUPS = ["pagerduty-observer"]
    DEFAULT_METADATA = {
        "system_type": "incident_management",
        "role": "observer"
    }


if __name__ == "__main__":
    PagerDutySystem().run()