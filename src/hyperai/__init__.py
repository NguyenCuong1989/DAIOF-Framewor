"""
HYPERAI Framework - Digital Organism System
============================================

A framework for creating self-evolving, self-maintaining AI entities
Philosophy: Biological principles applied to digital systems

Creator & Copyright Holder: Nguyễn Đức Cường (alpha_prime_omega)
Verification Code: 4287
Original Creation Date: October 30, 2025

MIT License: https://opensource.org/licenses/MIT
"""

__version__ = "1.0.0"
__author__ = "Nguyễn Đức Cường (alpha_prime_omega)"
__copyright__ = "Copyright (c) 2025 Nguyễn Đức Cường"

# Component imports
from .components.genome import DigitalGenome
from .components.metabolism import DigitalMetabolism
from .components.nervous_system import DigitalNervousSystem
from .components.organism import DigitalOrganism
# Core imports
from .core.haios_core import HAIOSCore
from .core.haios_runtime import HAIOSRuntime
# Ecosystem imports
from .ecosystem.ecosystem import DigitalEcosystem
from .protocols.dr_protocol import DRProtocol
# Metadata imports
from .protocols.metadata import CreatorHierarchy, HAIOSInvariants
# Protocol imports
from .protocols.symphony import ControlMetaData, SymphonyControlCenter

__all__ = [
    # Core
    "HAIOSCore",
    "HAIOSRuntime",
    # Components
    "DigitalGenome",
    "DigitalMetabolism",
    "DigitalNervousSystem",
    "DigitalOrganism",
    # Ecosystem
    "DigitalEcosystem",
    # Protocols
    "SymphonyControlCenter",
    "ControlMetaData",
    "DRProtocol",
    # Metadata
    "HAIOSInvariants",
    "CreatorHierarchy",
]
