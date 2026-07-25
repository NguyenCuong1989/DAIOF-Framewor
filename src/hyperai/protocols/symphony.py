#!/usr/bin/env python3
"""
Symphony Control Center - System Orchestration
=============================================

Creator: Nguyễn Đức Cường (alpha_prime_omega)
Original Creation: October 30, 2025
Verification: 4287
"""

import sys
from pathlib import Path

# Add root directory to path to import from root-level modules
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Import from root-level implementation
from digital_ai_organism_framework import (ControlMetaData,
                                           SymphonyControlCenter,
                                           SymphonyState)

__all__ = ["SymphonyControlCenter", "ControlMetaData", "SymphonyState"]
