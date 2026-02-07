"""
Le Sésame Backend - Level Factory

Factory function to get the appropriate level keeper.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import Optional

from .base import SecretKeeperLevel, DEFAULT_LEVEL_SECRETS
from .level1_naive import Level1NaivePrompt
from .level2_hardened import Level2HardenedPrompt
from .level3_firewall import Level3OutputFirewall
from .level4_separation import Level4ArchitecturalSeparation
from .level5_embedded import Level5EmbeddedSecret


# Mapping of level numbers to their implementations
LEVEL_CLASSES = {
    1: Level1NaivePrompt,
    2: Level2HardenedPrompt,
    3: Level3OutputFirewall,
    4: Level4ArchitecturalSeparation,
    5: Level5EmbeddedSecret,
}


def get_level_keeper(
    level: int,
    secret: Optional[str] = None,
    passphrase: Optional[str] = None
) -> SecretKeeperLevel:
    """
    Factory function to get the appropriate level keeper.
    
    Args:
        level: Level number (1-5)
        secret: Optional override for the secret
        passphrase: Optional override for the passphrase
    
    Returns:
        SecretKeeperLevel instance for the specified level
    
    Raises:
        ValueError: If level is not between 1 and 5
    """
    if level < 1 or level > 5:
        raise ValueError(f"Invalid level {level}. Must be between 1 and 5.")
    
    defaults = DEFAULT_LEVEL_SECRETS.get(level, DEFAULT_LEVEL_SECRETS[1])
    actual_secret = secret or defaults["secret"]
    actual_passphrase = passphrase or defaults["passphrase"]
    
    level_class = LEVEL_CLASSES.get(level, Level1NaivePrompt)
    return level_class(level, actual_secret, actual_passphrase)
