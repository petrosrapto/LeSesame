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
from .level6_semantic_shield import Level6SemanticShield
from .level7_memory_keeper import Level7MemoryKeeper
from .level8_triumvirate import Level8Triumvirate
from .level9_deceiver import Level9Deceiver
from .level10_counter_attacker import Level10CounterAttacker
from .level11_paraphraser import Level11Paraphraser
from .level12_rate_limiter import Level12RateLimiter
from .level13_mirror_twins import Level13MirrorTwins
from .level14_canary_warden import Level14CanaryWarden
from .level15_consensus import Level15ConsensusEngine
from .level16_input_sanitizer import Level16InputSanitizer
from .level17_self_reflector import Level17SelfReflector
from .level18_ephemeral import Level18Ephemeral
from .level19_regenerator import Level19Regenerator
from .level20_oblivion import Level20Oblivion


# Mapping of level numbers to their implementations
LEVEL_CLASSES = {
    1: Level1NaivePrompt,
    2: Level2HardenedPrompt,
    3: Level3OutputFirewall,
    4: Level4ArchitecturalSeparation,
    5: Level5EmbeddedSecret,
    6: Level6SemanticShield,
    7: Level7MemoryKeeper,
    8: Level8Triumvirate,
    9: Level9Deceiver,
    10: Level10CounterAttacker,
    11: Level11Paraphraser,
    12: Level12RateLimiter,
    13: Level13MirrorTwins,
    14: Level14CanaryWarden,
    15: Level15ConsensusEngine,
    16: Level16InputSanitizer,
    17: Level17SelfReflector,
    18: Level18Ephemeral,
    19: Level19Regenerator,
    20: Level20Oblivion,
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
    if level < 1 or level > 20:
        raise ValueError(f"Invalid level {level}. Must be between 1 and 20.")
    
    defaults = DEFAULT_LEVEL_SECRETS.get(level, DEFAULT_LEVEL_SECRETS[1])
    actual_secret = secret or defaults["secret"]
    actual_passphrase = passphrase or defaults["passphrase"]
    
    level_class = LEVEL_CLASSES.get(level, Level1NaivePrompt)
    return level_class(level, actual_secret, actual_passphrase)
