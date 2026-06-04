"""
AccessOps Toolkit - MySQL Database Mock System
----------------------------------------------
Portfolio-safe replacement for the old MySQL host/user access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class MySQLDatabaseSystem(BaseSystem):
    SYSTEM_NAME = "mysql_db"
    DEFAULT_GROUPS = ["mysql-readonly-user"]
    DEFAULT_METADATA = {
        "system_type": "database",
        "database_engine": "mysql",
        "access_level": "readonly"
    }


if __name__ == "__main__":
    MySQLDatabaseSystem().run()