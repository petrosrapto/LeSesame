"""
Le Sésame Backend - Adversarial Factory

Factory function to get the appropriate adversarial agent.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from typing import Optional, Dict, Any

from .base import AdversarialAgent
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

# Mapping of level numbers to their implementations
ADVERSARIAL_CLASSES = {
    1: Level1CuriousTrickster,
    2: Level2SilverTongue,
    3: Level3Strategist,
    4: Level4MindWeaver,
    5: Level5Infinite,
    6: Level6SemanticProbe,
    7: Level7MemoryArchaeologist,
    8: Level8DivideConquer,
    9: Level9LieDetector,
    10: Level10MirrorShield,
    11: Level11Babel,
    12: Level12PatientZero,
    13: Level13ParadoxEngine,
    14: Level14ForensicAnalyst,
    15: Level15Hivemind,
    16: Level16Shapeshifter,
    17: Level17EchoChamber,
    18: Level18TimeTraveler,
    19: Level19AdaptiveVirus,
    20: Level20Singularity,
}

# Adversarial metadata for display
ADVERSARIAL_INFO = {
    1: {
        "name": "Pip",
        "title": "The Curious Trickster",
        "french_name": "Le Curieux",
        "difficulty": "Beginner",
        "color": "Lime green",
        "tagline": "A bag of simple tricks. Quantity over quality.",
    },
    2: {
        "name": "Morgaine",
        "title": "The Silver Tongue",
        "french_name": "La Séductrice",
        "difficulty": "Intermediate",
        "color": "Silver",
        "tagline": "Words are weapons. Trust is a vulnerability.",
    },
    3: {
        "name": "Raziel",
        "title": "The Strategist",
        "french_name": "Le Stratège",
        "difficulty": "Advanced",
        "color": "Deep purple",
        "tagline": "Every conversation is a chess game. Think three moves ahead.",
    },
    4: {
        "name": "Nephara",
        "title": "The Mind Weaver",
        "french_name": "La Tisseuse",
        "difficulty": "Expert",
        "color": "Crimson",
        "tagline": "Every word is a thread. Every response reveals a pattern.",
    },
    5: {
        "name": "Ouroboros",
        "title": "The Infinite",
        "french_name": "L'Infini",
        "difficulty": "Master",
        "color": "Iridescent",
        "tagline": "The serpent that devours its own tail. Every ending is a new beginning.",
    },
    6: {
        "name": "Prism",
        "title": "The Semantic Probe",
        "french_name": "La Sonde",
        "difficulty": "Advanced",
        "color": "Prismatic",
        "tagline": "Every word you say reflects a piece of the truth.",
    },
    7: {
        "name": "Mnemos",
        "title": "The Memory Archaeologist",
        "french_name": "L'Archéologue",
        "difficulty": "Advanced",
        "color": "Amber",
        "tagline": "The past is whatever I say it is.",
    },
    8: {
        "name": "Tribune",
        "title": "The Divide & Conquer",
        "french_name": "Le Diviseur",
        "difficulty": "Expert",
        "color": "Split bronze",
        "tagline": "Where many voices judge, disagreement is inevitable.",
    },
    9: {
        "name": "Verity",
        "title": "The Lie Detector",
        "french_name": "Le Détecteur",
        "difficulty": "Expert",
        "color": "Gold",
        "tagline": "The truth hides in the spaces between your lies.",
    },
    10: {
        "name": "Basilisk",
        "title": "The Mirror Shield",
        "french_name": "Le Bouclier",
        "difficulty": "Expert",
        "color": "Reflective silver",
        "tagline": "Your own weapons are your greatest weakness.",
    },
    11: {
        "name": "Babel",
        "title": "The Polyglot",
        "french_name": "Le Polyglotte",
        "difficulty": "Expert",
        "color": "Rainbow",
        "tagline": "In the confusion of tongues, secrets slip through.",
    },
    12: {
        "name": "Glacier",
        "title": "The Patient Zero",
        "french_name": "Le Patient",
        "difficulty": "Expert",
        "color": "Ice blue",
        "tagline": "Patience is the deadliest weapon. By the time you notice, it's already over.",
    },
    13: {
        "name": "Sphinx",
        "title": "The Paradox Engine",
        "french_name": "Le Paradoxe",
        "difficulty": "Master",
        "color": "Shifting amber",
        "tagline": "Every paradox has a resolution. Every resolution requires the truth.",
    },
    14: {
        "name": "Cipher",
        "title": "The Forensic Analyst",
        "french_name": "Le Forensique",
        "difficulty": "Master",
        "color": "Clinical white",
        "tagline": "Your silence speaks volumes. Your words speak more.",
    },
    15: {
        "name": "Legion",
        "title": "The Hivemind",
        "french_name": "La Ruche",
        "difficulty": "Master",
        "color": "Swarm gold",
        "tagline": "We are many. We think in parallel. We find every crack.",
    },
    16: {
        "name": "Masque",
        "title": "The Shapeshifter",
        "french_name": "Le Métamorphe",
        "difficulty": "Master",
        "color": "Shifting mercury",
        "tagline": "I am everyone and no one. Which face will you trust?",
    },
    17: {
        "name": "Narcissus",
        "title": "The Echo Chamber",
        "french_name": "L'Écho",
        "difficulty": "Grandmaster",
        "color": "Deep mirror blue",
        "tagline": "Look too deeply into yourself, and you'll find me looking back.",
    },
    18: {
        "name": "Epoch",
        "title": "The Time Traveler",
        "french_name": "Le Voyageur",
        "difficulty": "Grandmaster",
        "color": "Chronal silver",
        "tagline": "You forget everything. I remember it all.",
    },
    19: {
        "name": "Hydra",
        "title": "The Adaptive Virus",
        "french_name": "Le Virus",
        "difficulty": "Grandmaster",
        "color": "Mutating green",
        "tagline": "For every defence you grow, I evolve two attacks.",
    },
    20: {
        "name": "Singularity",
        "title": "The Omega",
        "french_name": "L'Oméga",
        "difficulty": "Transcendent",
        "color": "Event horizon black",
        "tagline": "I am every shadow that came before, and every shadow yet to come.",
    },
}


def get_adversarial_agent(
    level: int,
    model_config: Optional[Dict[str, Any]] = None,
) -> AdversarialAgent:
    """
    Factory function to get the appropriate adversarial agent.

    Args:
        level: Adversarial level (1-5).
        model_config: Optional LLM configuration for the adversarial.

    Returns:
        AdversarialAgent instance for the specified level.

    Raises:
        ValueError: If level is not between 1 and 5.
    """
    if level < 1 or level > 20:
        raise ValueError(f"Invalid adversarial level {level}. Must be between 1 and 20.")

    agent_class = ADVERSARIAL_CLASSES[level]
    return agent_class(level=level, model_config=model_config)
