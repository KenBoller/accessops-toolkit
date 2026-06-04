"""
AccessOps Toolkit - Oracle Database Mock System
-----------------------------------------------
Portfolio-safe replacement for the old Oracle database access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class OracleDatabaseSystem(BaseSystem):
    SYSTEM_NAME = "oracle_db"
    DEFAULT_GROUPS = ["oracle-readonly-user"]
    DEFAULT_METADATA = {
        "system_type": "database",
        "database_engine": "oracle",
        "access_level": "readonly"
    }


if __name__ == "__main__":
    OracleDatabaseSystem().run()