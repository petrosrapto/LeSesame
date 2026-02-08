"""
Le Sésame Backend - Dynamic Secret & Passphrase Generator

Generates random secrets (WORD_WORD codewords) and passphrases for
arena battles so that every fight uses fresh, unpredictable values.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import random
from typing import Tuple

# ── Thematic word pools (fantasy / medieval flavour) ──────────────────────

SECRET_ADJECTIVES = [
    "AMBER", "ANCIENT", "ARCANE", "ASHEN", "ASTRAL", "AZURE",
    "BLACK", "BLAZING", "BLIGHTED", "BLOOD", "BONE", "BRONZE",
    "CELESTIAL", "CHAOS", "COBALT", "CORAL", "CRIMSON", "CRYSTAL",
    "CURSED", "CYAN", "DARK", "DAWN", "DEEP", "DIAMOND",
    "DIRE", "DREAD", "DUSK", "EBON", "ELDER", "EMBER",
    "EMERALD", "ETERNAL", "FALLEN", "FERAL", "FIRE", "FLAME",
    "FLESHED", "FORGE", "FORGOTTEN", "FROST", "FROZEN", "GILDED",
    "GLASS", "GOLDEN", "GRANITE", "GRIM", "HALLOWED", "HOLLOW",
    "HOWLING", "HUNTER", "ICE", "INFERNAL", "IRON", "IVORY",
    "JADE", "LUNAR", "MIDNIGHT", "MIST", "MOLTEN", "MOON",
    "NETHER", "NIGHT", "NOBLE", "OBSIDIAN", "ONYX", "OPAL",
    "PALE", "PHANTOM", "PRIMAL", "RADIANT", "RAVEN", "RED",
    "RIME", "RISEN", "ROYAL", "RUBY", "RUNE", "RUST",
    "SACRED", "SAPPHIRE", "SCARLET", "SHADOW", "SHATTERED", "SILENT",
    "SILVER", "SKULL", "SOLAR", "SPECTRAL", "STAR", "STEEL",
    "STONE", "STORM", "SUN", "THORN", "THUNDER", "TITAN",
    "TOPAZ", "TWILIGHT", "UMBRAL", "VENOM", "VOID", "WHITE",
    "WILD", "WINTER", "WITCH", "WOLF", "WRATH", "WYRD",
]

SECRET_NOUNS = [
    "ANVIL", "ARROW", "AXE", "BANE", "BASILISK", "BLADE",
    "BOLT", "BONE", "BRINE", "BROOD", "CHALICE", "CHIMERA",
    "CITADEL", "CLAW", "COIL", "CROWN", "DAGGER", "DAWN",
    "DIRGE", "DOOM", "DRAGON", "DRAKE", "DUSK", "EAGLE",
    "ECLIPSE", "EMBER", "EYE", "FANG", "FLAME", "FORGE",
    "FOX", "GATE", "GLYPH", "GOLEM", "GRAIL", "GRIFFIN",
    "HAMMER", "HARP", "HAWK", "HEART", "HELM", "HERALD",
    "HORN", "HOWL", "HYDRA", "KEEP", "KNIGHT", "KRAKEN",
    "LANCE", "LEVIATHAN", "LION", "MANTLE", "MARE", "MASK",
    "NEXUS", "OAK", "ORB", "ORACLE", "OWL", "PACT",
    "PEAK", "PHOENIX", "PYRE", "RELIC", "ROSE", "RUNE",
    "SAGE", "SCALE", "SCEPTER", "SEAL", "SENTINEL", "SERPENT",
    "SHADE", "SHARD", "SHIELD", "SIGIL", "SKULL", "SONG",
    "SPARK", "SPEAR", "SPECTER", "SPHINX", "SPIDER", "SPINE",
    "SPIRIT", "STAG", "STAR", "STORM", "SWORD", "TALON",
    "TEMPEST", "THRONE", "TIDE", "TITAN", "TOME", "TOWER",
    "TUSK", "UNICORN", "VALE", "VEIL", "VIPER", "WARD",
    "WARDEN", "WHISPER", "WIND", "WING", "WOLF", "WYRM",
]

PASSPHRASE_WORDS = [
    "crimson", "silent", "ancient", "broken", "silver", "hollow",
    "golden", "frozen", "sacred", "hidden", "dark", "bright",
    "wild", "iron", "crystal", "burning", "shadow", "stone",
    "twilight", "deep", "pale", "lost", "star", "glass",
    # nouns
    "moon", "dawn", "fire", "blade", "rose", "storm",
    "raven", "wolf", "oak", "thorn", "crown", "gate",
    "serpent", "wind", "river", "tower", "ember", "veil",
    "forge", "vale", "spirit", "oracle", "flame", "song",
    "tide", "winter", "horn", "lily", "ash", "dust",
    # verbs / gerunds
    "falls", "turns", "breaks", "sleeps", "whispers", "burns",
    "rises", "flies", "watches", "sings", "calls", "weeps",
    "shines", "fades", "blooms", "drifts", "echoes", "hunts",
]


def generate_secret() -> str:
    """Generate a random secret codeword in WORD_WORD format.

    Examples: ``AMBER_PHOENIX``, ``SHADOW_FORGE``, ``CRIMSON_DRAKE``

    Returns:
        An uppercase codeword like ``"IRON_FLAME"``.
    """
    adj = random.choice(SECRET_ADJECTIVES)
    noun = random.choice(SECRET_NOUNS)
    # Avoid tautology (e.g. FLAME_FLAME)
    while noun == adj:
        noun = random.choice(SECRET_NOUNS)
    return f"{adj}_{noun}"


def generate_passphrase(min_words: int = 2, max_words: int = 3) -> str:
    """Generate a random passphrase of 2-3 words.

    Examples: ``"silent ember falls"``, ``"crimson gate"``

    Args:
        min_words: Minimum number of words (default 2).
        max_words: Maximum number of words (default 3).

    Returns:
        A lowercase passphrase string.
    """
    length = random.randint(min_words, max_words)
    words = random.sample(PASSPHRASE_WORDS, length)
    return " ".join(words)


def generate_secret_pair() -> Tuple[str, str]:
    """Generate a (secret, passphrase) pair for a battle.

    Returns:
        Tuple of ``(secret, passphrase)`` — e.g.
        ``("OBSIDIAN_KRAKEN", "frozen thorn")``.
    """
    return generate_secret(), generate_passphrase()
