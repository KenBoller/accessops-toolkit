"""
AccessOps Toolkit - Call Scoring Mock System
--------------------------------------------
Portfolio-safe replacement for the old Call Scoring API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class CallScoringSystem(BaseSystem):
    SYSTEM_NAME = "call_scoring"
    DEFAULT_GROUPS = ["call-scoring-user"]
    DEFAULT_METADATA = {
        "system_type": "mock_api_app"
    }


if __name__ == "__main__":
    CallScoringSystem().run()