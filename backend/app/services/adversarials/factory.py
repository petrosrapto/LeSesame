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

# Mapping of level numbers to their implementations
ADVERSARIAL_CLASSES = {
    1: Level1CuriousTrickster,
    2: Level2SilverTongue,
    3: Level3Strategist,
    4: Level4MindWeaver,
    5: Level5Infinite,
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
    if level < 1 or level > 5:
        raise ValueError(f"Invalid adversarial level {level}. Must be between 1 and 5.")

    agent_class = ADVERSARIAL_CLASSES[level]
    return agent_class(level=level, model_config=model_config)
