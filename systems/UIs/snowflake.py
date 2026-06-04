"""
AccessOps Toolkit - Snowflake Mock System
-----------------------------------------
Portfolio-safe replacement for the old Snowflake SQL-backed access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class SnowflakeSystem(BaseSystem):
    SYSTEM_NAME = "snowflake"
    DEFAULT_GROUPS = ["snowflake-readonly-user"]
    DEFAULT_METADATA = {
        "system_type": "data_warehouse",
        "database_engine": "snowflake",
        "access_level": "readonly"
    }


if __name__ == "__main__":
    SnowflakeSystem().run()