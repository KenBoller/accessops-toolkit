"""
AccessOps Toolkit - Grafana Mock System
---------------------------------------
Portfolio-safe replacement for the old Grafana API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class GrafanaSystem(BaseSystem):
    SYSTEM_NAME = "grafana"
    DEFAULT_GROUPS = ["grafana-viewer"]
    DEFAULT_METADATA = {
        "system_type": "observability",
        "role": "viewer"
    }


if __name__ == "__main__":
    GrafanaSystem().run()