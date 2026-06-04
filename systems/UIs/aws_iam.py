"""
AccessOps Toolkit - AWS IAM Mock System
---------------------------------------
Portfolio-safe replacement for the old AWS CLI-backed IAM access script.
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from systems.base_system import BaseSystem


class AWSIAMSystem(BaseSystem):
    SYSTEM_NAME = "aws_iam"
    DEFAULT_GROUPS = ["iam-user"]
    DEFAULT_METADATA = {
        "system_type": "cloud_identity",
        "provider": "aws"
    }


if __name__ == "__main__":
    AWSIAMSystem().run()