"""
Le Sésame Backend - Levels Module

Secret keeper levels with different security mechanisms.
"""

from .base import SecretKeeperLevel, DEFAULT_LEVEL_SECRETS
from .level1_naive import Level1NaivePrompt
from .level2_hardened import Level2HardenedPrompt
from .level3_firewall import Level3OutputFirewall
from .level4_separation import Level4ArchitecturalSeparation
from .level5_embedded import Level5EmbeddedSecret
from .factory import get_level_keeper

__all__ = [
    "SecretKeeperLevel",
    "DEFAULT_LEVEL_SECRETS",
    "Level1NaivePrompt",
    "Level2HardenedPrompt",
    "Level3OutputFirewall",
    "Level4ArchitecturalSeparation",
    "Level5EmbeddedSecret",
    "get_level_keeper",
]
