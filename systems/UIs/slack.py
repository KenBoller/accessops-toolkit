"""
AccessOps Toolkit - Slack Mock System
-------------------------------------
Portfolio-safe replacement for the old Slack API-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class SlackSystem(BaseSystem):
    SYSTEM_NAME = "slack"
    DEFAULT_GROUPS = ["slack-member"]
    DEFAULT_METADATA = {
        "system_type": "team_communication",
        "role": "member"
    }


if __name__ == "__main__":
    SlackSystem().run()