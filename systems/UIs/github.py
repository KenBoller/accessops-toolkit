"""
AccessOps Toolkit - GitHub Mock System
--------------------------------------
Portfolio-safe replacement for the old GitHub organization access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class GitHubSystem(BaseSystem):
    SYSTEM_NAME = "github"
    DEFAULT_GROUPS = ["github-member"]
    DEFAULT_METADATA = {
        "system_type": "source_control",
        "provider": "github",
        "role": "member"
    }


if __name__ == "__main__":
    GitHubSystem().run()