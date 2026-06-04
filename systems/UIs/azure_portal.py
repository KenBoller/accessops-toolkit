"""
AccessOps Toolkit - Azure Portal Mock System
--------------------------------------------
Portfolio-safe replacement for the old Azure Graph-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class AzurePortalSystem(BaseSystem):
    SYSTEM_NAME = "azure_portal"
    DEFAULT_GROUPS = ["azure-portal-user"]
    DEFAULT_METADATA = {
        "system_type": "cloud_identity",
        "provider": "azure"
    }


if __name__ == "__main__":
    AzurePortalSystem().run()