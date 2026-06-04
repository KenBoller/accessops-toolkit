"""
AccessOps Toolkit - Chef Mock System
------------------------------------
Portfolio-safe replacement for the old Chef/knife DataBag access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class ChefSystem(BaseSystem):
    SYSTEM_NAME = "chef"
    DEFAULT_GROUPS = ["chef-user"]
    DEFAULT_METADATA = {
        "system_type": "configuration_management",
        "permissions": ["read", "execute"]
    }


if __name__ == "__main__":
    ChefSystem().run()