"""
AccessOps Toolkit - Jira Mock System
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class JiraSystem(BaseSystem):
    SYSTEM_NAME = "jira"
    DEFAULT_GROUPS = ["standard-user"]


if __name__ == "__main__":
    JiraSystem().run()