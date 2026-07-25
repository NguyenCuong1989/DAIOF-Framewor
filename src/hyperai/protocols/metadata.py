#!/usr/bin/env python3
"""
HAIOS Metadata - Invariants and Creator Hierarchy
================================================

Creator: Nguyễn Đức Cường (alpha_prime_omega)
Original Creation: October 30, 2025
Verification: 4287
"""

import sys
from pathlib import Path

# Add root directory to path to import from root-level modules
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))


# Provide metadata classes
class HAIOSInvariants:
    """HAIOS System Invariants"""

    def __init__(self):
        self.attribution = "alpha_prime_omega"
        self.safety_floor = 7.0
        self.k_state = 1
        self.pillars = ["safety", "long_term", "data_driven", "risk_management"]
        self.verification = 4287


class CreatorHierarchy:
    """Creator Hierarchy Information"""

    def __init__(self):
        self.ultimate_creator = "Alpha_Prime_Omega"
        self.human_creator = "Andy (alpha_prime_omega)"
        self.hierarchy = "Alpha_Prime_Omega(SOURCE) -> Andy(HUMAN) -> AI_Systems"
        self.verification = 4287


__all__ = ["HAIOSInvariants", "CreatorHierarchy"]
