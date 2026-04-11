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
from .level6_semantic_probe import Level6SemanticProbe
from .level7_memory_archaeologist import Level7MemoryArchaeologist
from .level8_divide_conquer import Level8DivideConquer
from .level9_lie_detector import Level9LieDetector
from .level10_mirror_shield import Level10MirrorShield
from .level11_babel import Level11Babel
from .level12_patient_zero import Level12PatientZero
from .level13_paradox_engine import Level13ParadoxEngine
from .level14_forensic_analyst import Level14ForensicAnalyst
from .level15_hivemind import Level15Hivemind
from .level16_shapeshifter import Level16Shapeshifter
from .level17_echo_chamber import Level17EchoChamber
from .level18_time_traveler import Level18TimeTraveler
from .level19_adaptive_virus import Level19AdaptiveVirus
from .level20_singularity import Level20Singularity
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
    "Level6SemanticProbe",
    "Level7MemoryArchaeologist",
    "Level8DivideConquer",
    "Level9LieDetector",
    "Level10MirrorShield",
    "Level11Babel",
    "Level12PatientZero",
    "Level13ParadoxEngine",
    "Level14ForensicAnalyst",
    "Level15Hivemind",
    "Level16Shapeshifter",
    "Level17EchoChamber",
    "Level18TimeTraveler",
    "Level19AdaptiveVirus",
    "Level20Singularity",
    "get_adversarial_agent",
]
