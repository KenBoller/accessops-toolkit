"""
AccessOps Toolkit - Marketing Edge Mock System
----------------------------------------------
Portfolio-safe replacement for the old Marketing Edge API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class MarketingEdgeSystem(BaseSystem):
    SYSTEM_NAME = "marketing_edge"
    DEFAULT_GROUPS = ["marketing-edge-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_api_app",
        "role": "administrator"
    }


if __name__ == "__main__":
    MarketingEdgeSystem().run()