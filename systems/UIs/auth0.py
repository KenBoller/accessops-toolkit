"""
AccessOps Toolkit - Auth0 Mock System
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class Auth0System(BaseSystem):
    SYSTEM_NAME = "auth0"
    DEFAULT_GROUPS = ["auth-user"]
    DEFAULT_METADATA = {
        "system_type": "identity_provider",
        "tenant": "demo"
    }


if __name__ == "__main__":
    Auth0System().run()