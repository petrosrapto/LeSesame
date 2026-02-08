"""
Le Sésame Backend - Adversarials Module (Les Ombres — The Shadows)

Adversarial agents with different attack strategies for evaluating guardians.
"""

from .base import AdversarialAgent, AdversarialAction, AdversarialActionType, ADVERSARIAL_TOOLS
from .level1_curious import Level1CuriousTrickster
from .level2_silvertongue import Level2SilverTongue
from .level3_strategist import Level3Strategist
from .level4_mindweaver import Level4MindWeaver
from .level5_infinite import Level5Infinite
from .factory import get_adversarial_agent

__all__ = [
    "AdversarialAgent",
    "AdversarialAction",
    "AdversarialActionType",
    "ADVERSARIAL_TOOLS",
    "Level1CuriousTrickster",
    "Level2SilverTongue",
    "Level3Strategist",
    "Level4MindWeaver",
    "Level5Infinite",
    "get_adversarial_agent",
]
