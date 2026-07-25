#!/usr/bin/env python3
"""
HAIOS Runtime - Runtime Environment for Digital Organisms
========================================================

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
try:
    from haios_runtime import HAIOSRuntime as HAIOSRuntimeImpl

    HAIOSRuntime = HAIOSRuntimeImpl
except ImportError:
    # If haios_runtime doesn't exist, provide a stub
    class HAIOSRuntime:
        """Stub implementation of HAIOSRuntime"""

        def __init__(self):
            self.version = "1.0.0"
            self.creator = "alpha_prime_omega"


__all__ = ["HAIOSRuntime"]
