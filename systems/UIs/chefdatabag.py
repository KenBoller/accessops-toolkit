"""
AccessOps Toolkit - Chef DataBag Mock System
--------------------------------------------
Portfolio-safe replacement for the old GitHub-backed Chef DataBag access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class ChefDataBagSystem(BaseSystem):
    SYSTEM_NAME = "chefdatabag"
    DEFAULT_GROUPS = ["chef-databag-user"]
    DEFAULT_METADATA = {
        "system_type": "configuration_repository",
        "repository_type": "git"
    }


if __name__ == "__main__":
    ChefDataBagSystem().run()