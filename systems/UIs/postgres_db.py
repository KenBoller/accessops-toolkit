"""
AccessOps Toolkit - PostgreSQL Database Mock System
---------------------------------------------------
Portfolio-safe replacement for the old PostgreSQL multi-host access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class PostgresDatabaseSystem(BaseSystem):
    SYSTEM_NAME = "postgres_db"
    DEFAULT_GROUPS = ["postgres-readonly-user"]
    DEFAULT_METADATA = {
        "system_type": "database",
        "database_engine": "postgresql",
        "access_level": "readonly"
    }


if __name__ == "__main__":
    PostgresDatabaseSystem().run()