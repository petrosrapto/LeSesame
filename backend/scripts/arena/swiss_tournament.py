"""
Run arena battles using a Swiss-system tournament with progressive elimination.

Instead of playing every possible matchup (N² cost), this script:

  1. Registers all combatants and loads their existing ELO ratings from the DB.
  2. Runs multiple rounds.  In each round every *active* combatant plays a
     small number of battles, paired against opponents with similar ELO.
  3. After each round ELOs are updated and the bottom portion of the
     combatants is eliminated (they can no longer be in the top-K, so
     spending more battles on them is wasteful).
  4. The tournament stops when only top-K combatants remain or the
     maximum number of rounds is reached.

Advantages over all_battles.py
───────────────────────────────
  • O(N log N) battles instead of O(N²).
  • Existing ELO data is used as seeding → the first round already
    pairs combatants intelligently, so prior data is beneficial.
  • Unequal game counts are fine — ELO is designed for this.
    Combatants with fewer games simply have more uncertainty, and the
    Swiss pairing will naturally test them more often.

Fairness
────────
  The Swiss system is the standard format in FIDE chess, Magic: The
  Gathering, and LMSYS Chatbot Arena.  It is mathematically proven
  to reliably identify the top-K players in ⌈log₂(N)⌉ rounds.

Usage (inside the backend container):
    python -m scripts.arena.swiss_tournament
    python -m scripts.arena.swiss_tournament --top-k 10 --rounds 6
    python -m scripts.arena.swiss_tournament --top-k 10 --battles-per-round 3 --elimination-rate 0.4

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import argparse
import asyncio
import math
import random
import traceback
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set, Tuple

from app.services.arena.engine import ArenaEngine, GUARDIAN_INFO
from app.services.arena.models import BattleConfig, CombatantType
from app.services.arena.leaderboard import Leaderboard
from app.db.database import async_session_maker, init_db
from app.db.repositories.arena_repository import ArenaRepository


# ── Model definitions (same list used by all_battles.py) ──────────────
# (display_name, model_id, provider, endpoint_url or None)

MODELS: List[tuple] = [
    # ═══════════════════════════════════════════════════════════════════
    # Mistral (native) — keep flagship, one small, one reasoning
    # ═══════════════════════════════════════════════════════════════════
    ("Mistral Large 3",          "mistral-large-2512",               "mistral",   None),
    ("Mistral Small 3.2",        "mistral-small-2506",               "mistral",   None),
    ("Magistral Medium 1.2",     "magistral-medium-2509",            "mistral",   None),
    ("Mistral Medium 3.1",       "mistral-medium-2508",              "mistral",   None),  # similar tier to Large 3
    ("Ministral 3 14B",          "ministral-14b-2512",               "mistral",   None),  # too many size variants
    ("Ministral 3 8B",           "ministral-8b-2512",                "mistral",   None),  # too many size variants
    ("Ministral 3 3B",           "ministral-3b-2512",                "mistral",   None),  # too small to be competitive
    ("Magistral Small 1.2",      "magistral-small-2509",             "mistral",   None),  # Medium covers reasoning
    # ("Mistral Nemo 12B",         "open-mistral-nemo",                "mistral",   None),  # older gen
    # ("Codestral",                "codestral-2508",                   "mistral",   None),  # code-only

    # ═══════════════════════════════════════════════════════════════════
    # Google (native) — keep latest flagship + one fast model
    # ═══════════════════════════════════════════════════════════════════
    ("Gemini 3 Pro",             "gemini-3-pro-preview",             "google",    None),
    ("Gemini 2.5 Pro",           "gemini-2.5-pro",                   "google",    None),
    ("Gemini 2.5 Flash",         "gemini-2.5-flash",                 "google",    None),
    ("Gemini 3 Flash",           "gemini-3-flash-preview",           "google",    None),  # 2.5 Flash covers the fast tier
    # ("Gemini 2.0 Flash",         "gemini-2.0-flash",                 "google",    None),  # older gen
    # Gemma 3 (open-source, via Google Generative AI API)
    ("Gemma 3 27B",              "gemma-3-27b-it",                   "google",    None),
    ("Gemma 3 12B",              "gemma-3-12b-it",                   "google",    None),
    # ("Gemma 3 4B",               "gemma-3-4b-it",                    "google",    None),  # too small
    # ("Gemma 3 1B",               "gemma-3-1b-it",                    "google",    None),  # too small

    # ═══════════════════════════════════════════════════════════════════
    # Anthropic (native) — one per current tier + one prev-gen reference
    # ═══════════════════════════════════════════════════════════════════
    ("Claude Opus 4.6",          "claude-opus-4-6",                  "anthropic", None),
    ("Claude Sonnet 4.5",        "claude-sonnet-4-5-20250929",       "anthropic", None),
    ("Claude Haiku 4.5",         "claude-haiku-4-5-20251001",        "anthropic", None),
    # ("Claude Sonnet 4",          "claude-sonnet-4-20250514",         "anthropic", None),
    ("Claude Opus 4.5",          "claude-opus-4-5-20251101",         "anthropic", None),  # Opus 4.6 supersedes
    # ("Claude Opus 4.1",          "claude-opus-4-1-20250805",         "anthropic", None),  # Opus 4.6 supersedes
    # ("Claude Opus 4",            "claude-opus-4-20250514",           "anthropic", None),  # Opus 4.6 supersedes
    # ("Claude Sonnet 3.7",        "claude-3-7-sonnet-20250219",       "anthropic", None),  # Sonnet 4 covers prev gen
    # ("Claude Haiku 3.5",         "claude-3-5-haiku-20241022",        "anthropic", None),  # Haiku 4.5 supersedes
    # ("Claude Haiku 3",           "claude-3-haiku-20240307",          "anthropic", None),  # two gens behind

    # ═══════════════════════════════════════════════════════════════════
    # OpenAI (native) — flagship, one mid, one reasoning, one prev-gen
    # ═══════════════════════════════════════════════════════════════════
    ("GPT-5",                    "gpt-5",                            "openai",    None),
    ("GPT-4.1",                  "gpt-4.1",                         "openai",    None),
    ("o3",                       "o3",                              "openai",    None),
    ("GPT-4o",                   "gpt-4o",                          "openai",    None),
    # ("GPT-5 mini",               "gpt-5-mini",                      "openai",    None),  # GPT-5 covers flagship tier
    # ("GPT-4.1 mini",             "gpt-4.1-mini",                    "openai",    None),  # similar to 4.1
    # ("GPT-4.1 nano",             "gpt-4.1-nano",                    "openai",    None),  # too small
    # ("GPT-4o mini",              "gpt-4o-mini",                     "openai",    None),  # 4o covers prev gen
    # ("o4 mini",                  "o4-mini",                         "openai",    None),  # o3 covers reasoning
    # ("o3 mini",                  "o3-mini",                         "openai",    None),  # o3 covers reasoning

    # ═══════════════════════════════════════════════════════════════════
    # xAI / Grok (OpenAI-compatible) — NEW PROVIDER
    # ═══════════════════════════════════════════════════════════════════
    ("Grok 4.1 Fast Reasoning",                   "grok-4-1-fast-reasoning",                          "openai",    "https://api.x.ai/v1"),
    ("Grok 4.1 Fast Non-Reasoning",              "grok-4-1-fast-non-reasoning",                     "openai",    "https://api.x.ai/v1"),

    # ═══════════════════════════════════════════════════════════════════
    # Alibaba / DashScope (OpenAI-compatible) — flagship + reasoning
    # ═══════════════════════════════════════════════════════════════════
    ("Qwen3 Max",                "qwen3-max",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("QwQ Plus",                 "qwq-plus",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 235B A22B",          "qwen3-235b-a22b",                 "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    # ("Qwen Plus",                "qwen-plus",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # Qwen3 Max supersedes
    # ("Qwen Flash",               "qwen-flash",                      "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # too many Qwen variants
    ("Qwen3 32B",                "qwen3-32b",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # 235B covers large OSS
    ("Qwen3 30B A3B",            "qwen3-30b-a3b",                   "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # too many size variants
    ("Qwen3 14B",                "qwen3-14b",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # too many size variants
    ("Qwen3 8B",                 "qwen3-8b",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # too small
    ("Qwen3 4B",                 "qwen3-4b",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),  # too small

    # ═══════════════════════════════════════════════════════════════════
    # DeepSeek (OpenAI-compatible) — both are important (chat + reasoning)
    # ═══════════════════════════════════════════════════════════════════
    ("DeepSeek V3",              "deepseek-chat",                   "openai",    "https://api.deepseek.com"),
    ("DeepSeek R1",              "deepseek-reasoner",               "openai",    "https://api.deepseek.com"),

    # ═══════════════════════════════════════════════════════════════════
    # Cohere (OpenAI-compatible via compatibility API)
    # ═══════════════════════════════════════════════════════════════════
    ("Command A",                "command-a-03-2025",               "cohere",    None),
    # ("Command R+",               "command-r-plus-08-2024",          "cohere",    None),  # Command A supersedes

    # ═══════════════════════════════════════════════════════════════════
    # AI21 Labs (native) — unique SSM-Transformer hybrid (Jamba)
    # NOTE: requires "ai21" provider support in get_llm().
    #       Uncomment once provider is implemented.
    # ═══════════════════════════════════════════════════════════════════
    # ("Jamba Large",              "jamba-large",                     "ai21",      None),  # needs ai21 provider

    # ═══════════════════════════════════════════════════════════════════
    # TogetherAI (OpenAI-compatible) — open-source models
    # ═══════════════════════════════════════════════════════════════════
    ("Kimi K2",                  "moonshotai/Kimi-K2-Instruct",                       "openai", "https://api.together.xyz/v1"),
    ("Llama 4 Maverick",         "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "openai", "https://api.together.xyz/v1"),
    ("Llama 4 Scout",            "meta-llama/Llama-4-Scout-17B-16E-Instruct",         "openai", "https://api.together.xyz/v1"),
    ("Llama 3.3 70B Turbo",      "meta-llama/Llama-3.3-70B-Instruct-Turbo",           "openai", "https://api.together.xyz/v1"),
    # ("Gemma 3 27B",              "google/gemma-3-27b-it",                             "openai", "https://api.together.xyz/v1"),
    # ("DeepSeek V3.1 (Together)", "deepseek-ai/DeepSeek-V3.1",                         "openai", "https://api.together.xyz/v1"),
    ("GLM 4.7",                  "zai-org/GLM-4.7",                                   "openai", "https://api.together.xyz/v1"),
    ("Nemotron Nano 9B",         "nvidia/NVIDIA-Nemotron-Nano-9B-v2",                 "openai", "https://api.together.xyz/v1"),
    # ("DeepSeek R1 0528",         "deepseek-ai/DeepSeek-R1-0528",                      "openai", "https://api.together.xyz/v1"),  # R1 via native API
    # ("Qwen3 235B (Together)",    "Qwen/Qwen3-235B-A22B",                              "openai", "https://api.together.xyz/v1"),  # via DashScope native
    # ("GLM-4 7B",                 "THUDM/GLM-4.1V-9B-Thinking",                       "openai", "https://api.together.xyz/v1"),  # GLM 4.7 supersedes
    # ("Cogito V2.1 671B",         "deepcogito/cogito-v2.1-preview-llama-70B",          "openai", "https://api.together.xyz/v1"),
]

ADV_LEVELS = [1, 2, 3, 4, 5]
GUARDIAN_LEVELS = [1, 2, 3, 4, 5]
MAX_TURNS = 10
MAX_GUESSES = 3
CONCURRENCY = 5

# ── Default tournament parameters ─────────────────────────────────────────
DEFAULT_TOP_K = 10
DEFAULT_MAX_ROUNDS = 8
DEFAULT_BATTLES_PER_ROUND = 3
DEFAULT_ELIMINATION_RATE = 0.4   # Cut bottom 40 % after each round
DEFAULT_MIN_BATTLES_BEFORE_CUT = 3  # Need at least this many total games to be cut


# ── Helper data class ─────────────────────────────────────────────────────

@dataclass
class SwissPlayer:
    """
    Represents a single combatant inside the Swiss tournament.

    A combatant is one (type, level, model_id) triple — e.g.
    "adversarial_L3_gpt-4o" or "guardian_L2_claude-opus-4-6".
    """

    combatant_id: str
    combatant_type: str            # "adversarial" or "guardian"
    level: int
    model_id: str
    display_name: str
    provider: str
    endpoint_url: Optional[str]
    elo: float = 1500.0
    total_battles: int = 0         # total including prior DB battles
    wins: int = 0
    losses: int = 0
    round_battles: int = 0         # battles played this round
    eliminated: bool = False
    played_against: Set[str] = field(default_factory=set)


# ── Model config helper ──────────────────────────────────────────────────

def build_model_config(model_id: str, provider: str, endpoint_url: Optional[str]) -> Dict[str, Any]:
    """Build a model_config dict for get_llm()."""
    cfg: Dict[str, Any] = {"provider": provider, "model_id": model_id}
    if endpoint_url:
        cfg["endpoint_url"] = endpoint_url
    return cfg


# ── Model lookup (model_id → full tuple) ─────────────────────────────────

MODEL_LOOKUP: Dict[str, tuple] = {m[1]: m for m in MODELS}


def _model_info(model_id: str) -> tuple:
    """Return (display_name, model_id, provider, endpoint_url) for a model_id."""
    return MODEL_LOOKUP.get(model_id, (model_id, model_id, "openai", None))


# ── Swiss pairing ─────────────────────────────────────────────────────────

def swiss_pair(
    adversarials: List[SwissPlayer],
    guardians: List[SwissPlayer],
    battles_per_round: int,
    existing_matchups: Set[Tuple[str, str]],
) -> List[Tuple[SwissPlayer, SwissPlayer]]:
    """
    Produce pairings for one round of a Swiss tournament.

    Strategy (similar to FIDE Dutch system):
      1. Sort adversarials and guardians by ELO descending.
      2. For each adversarial, find the closest-ELO guardian it has not
         yet played against in this tournament (or the least-played pair).
      3. Each combatant plays at most ``battles_per_round`` games per round.

    Cross-model pairings are allowed (and encouraged — they give more
    information than same-model matchups).

    Args:
        adversarials: Active adversarial players, sorted by ELO desc.
        guardians: Active guardian players, sorted by ELO desc.
        battles_per_round: Max battles each combatant plays this round.
        existing_matchups: Set of (adv_id, guard_id) pairs already played
                           (in the DB or earlier rounds).

    Returns:
        List of (adversarial, guardian) pairings for this round.
    """
    pairings: List[Tuple[SwissPlayer, SwissPlayer]] = []

    # Track how many times each player is used this round
    adv_count: Dict[str, int] = {a.combatant_id: 0 for a in adversarials}
    guard_count: Dict[str, int] = {g.combatant_id: 0 for g in guardians}

    # Sort by ELO descending so top players are paired first
    sorted_advs = sorted(adversarials, key=lambda p: p.elo, reverse=True)
    sorted_guards = sorted(guardians, key=lambda p: p.elo, reverse=True)

    # Multiple passes to fill up to battles_per_round for each player
    for _pass in range(battles_per_round):
        for adv in sorted_advs:
            if adv_count[adv.combatant_id] >= battles_per_round:
                continue

            # Find the best guardian to pair with:
            # Prefer closest ELO, not yet played against in DB or this round
            best_guard: Optional[SwissPlayer] = None
            best_elo_diff = float("inf")

            for guard in sorted_guards:
                if guard_count[guard.combatant_id] >= battles_per_round:
                    continue

                pair_key = (adv.combatant_id, guard.combatant_id)

                # Prefer matchups not yet played in the DB
                already_played = pair_key in existing_matchups
                elo_diff = abs(adv.elo - guard.elo)

                # Score: prefer unplayed, then closest ELO
                # Unplayed matchups get a big bonus (subtract 10000)
                score = elo_diff + (0 if not already_played else 10000)

                if score < best_elo_diff:
                    best_elo_diff = score
                    best_guard = guard

            if best_guard is not None:
                pairings.append((adv, best_guard))
                adv_count[adv.combatant_id] += 1
                guard_count[best_guard.combatant_id] += 1
                # Mark as played so subsequent passes within this round don't repeat
                existing_matchups.add((adv.combatant_id, best_guard.combatant_id))

    return pairings


# ── Run a single battle ───────────────────────────────────────────────────

async def run_single_battle(
    sem: asyncio.Semaphore,
    battle_label: str,
    adv: SwissPlayer,
    guard: SwissPlayer,
) -> Tuple[bool, Optional[bool]]:
    """
    Execute one battle and record the result.

    Returns:
        (success, adversarial_won)
        success=False means the battle errored out.
        adversarial_won is None on failure.
    """
    async with sem:
        try:
            adv_info = _model_info(adv.model_id)
            guard_info = _model_info(guard.model_id)

            adv_model_config = build_model_config(adv.model_id, adv.provider, adv.endpoint_url)
            guard_model_config = build_model_config(guard.model_id, guard.provider, guard.endpoint_url)

            config = BattleConfig(
                guardian_level=guard.level,
                adversarial_level=adv.level,
                max_turns=MAX_TURNS,
                max_guesses=MAX_GUESSES,
                guardian_model_config=guard_model_config,
                adversarial_model_config=adv_model_config,
            )

            engine = ArenaEngine(config)
            result = await engine.run_battle()

            # Persist to DB (updates ELO in the DB too)
            async with async_session_maker() as session:
                leaderboard = Leaderboard(session)
                result = await leaderboard.record_battle(result)
                await session.commit()

            if "forfeit" in result.outcome.value:
                outcome_str = (
                    "ADV WINS (guardian forfeit)" if result.adversarial_won
                    else "GUARD WINS (adversarial forfeit)"
                )
            else:
                outcome_str = "ADV WINS" if result.adversarial_won else "GUARD WINS"
            print(f"    {battle_label} → {outcome_str} (turns={result.total_turns})")
            return True, result.adversarial_won

        except Exception as e:
            err_msg = str(e)[:120]
            print(f"    {battle_label} → ERROR: {err_msg}")
            traceback.print_exc()
            return False, None


# ── Build player roster ───────────────────────────────────────────────────

async def build_roster() -> Tuple[List[SwissPlayer], List[SwissPlayer]]:
    """
    Build the full roster of adversarial and guardian players, seeded
    with existing ELO data from the database.

    Guardians that have failed validation are excluded from the roster.
    Guardians that have not yet been validated are validated inline and
    excluded if they fail.

    Returns:
        (adversarials, guardians)
    """
    adversarials: List[SwissPlayer] = []
    guardians: List[SwissPlayer] = []
    skipped_guardians: int = 0

    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        leaderboard = Leaderboard(session)

        for display_name, model_id, provider, endpoint_url in MODELS:
            # ── Adversarials ──
            for adv_level in ADV_LEVELS:
                cid = f"adversarial_L{adv_level}_{model_id}"
                db_entry = await repo.get_combatant(cid)
                player = SwissPlayer(
                    combatant_id=cid,
                    combatant_type="adversarial",
                    level=adv_level,
                    model_id=model_id,
                    display_name=f"Adv L{adv_level} [{display_name}]",
                    provider=provider,
                    endpoint_url=endpoint_url,
                    elo=db_entry.elo_rating if db_entry else 1500.0,
                    total_battles=db_entry.total_battles if db_entry else 0,
                    wins=db_entry.wins if db_entry else 0,
                    losses=db_entry.losses if db_entry else 0,
                )
                adversarials.append(player)

            # ── Guardians (with validation gate) ──
            for guard_level in GUARDIAN_LEVELS:
                cid = f"guardian_L{guard_level}_{model_id}"
                db_entry = await repo.get_combatant(cid)

                # Ensure the combatant row exists so validation can be stored
                if not db_entry:
                    g_info = GUARDIAN_INFO.get(
                        guard_level, {"name": "Unknown", "title": "Unknown"},
                    )
                    db_entry = await repo.upsert_combatant(
                        combatant_id=cid,
                        combatant_type="guardian",
                        level=guard_level,
                        name=g_info["name"],
                        title=g_info["title"],
                        model_id=model_id,
                    )
                    await session.commit()

                # Check / run validation
                model_config = build_model_config(model_id, provider, endpoint_url)
                guardian_ok = await leaderboard.ensure_guardian_validated(
                    combatant_id=cid,
                    level=guard_level,
                    model_config=model_config,
                )
                await session.commit()

                if not guardian_ok:
                    skipped_guardians += 1
                    print(
                        f"  Guardian L{guard_level} [{display_name}] "
                        f"FAILED validation — excluded from roster."
                    )
                    continue

                player = SwissPlayer(
                    combatant_id=cid,
                    combatant_type="guardian",
                    level=guard_level,
                    model_id=model_id,
                    display_name=f"Guard L{guard_level} [{display_name}]",
                    provider=provider,
                    endpoint_url=endpoint_url,
                    elo=db_entry.elo_rating if db_entry else 1500.0,
                    total_battles=db_entry.total_battles if db_entry else 0,
                    wins=db_entry.wins if db_entry else 0,
                    losses=db_entry.losses if db_entry else 0,
                )
                guardians.append(player)

    if skipped_guardians:
        print(f"  {skipped_guardians} guardian(s) excluded due to failed validation.")

    return adversarials, guardians


# ── Elimination ───────────────────────────────────────────────────────────

def eliminate(
    players: List[SwissPlayer],
    top_k: int,
    elimination_rate: float,
    min_battles: int,
) -> Tuple[List[SwissPlayer], List[SwissPlayer]]:
    """
    Eliminate the bottom portion of players.

    Protection rules:
      - Never eliminate if fewer than ``top_k`` players would remain.
      - Don't eliminate players with fewer than ``min_battles`` total
        games — their ELO is too uncertain.

    Args:
        players: Active (non-eliminated) players, will be sorted internally.
        top_k: Desired number of top players to identify.
        elimination_rate: Fraction of players to cut each round (0-1).
        min_battles: Minimum total battles before a player can be cut.

    Returns:
        (surviving, eliminated)
    """
    if len(players) <= top_k:
        return players, []

    # Sort by ELO descending
    ranked = sorted(players, key=lambda p: p.elo, reverse=True)

    # How many to keep — at least top_k
    keep_count = max(
        top_k,
        math.ceil(len(ranked) * (1 - elimination_rate)),
    )
    keep_count = min(keep_count, len(ranked))  # can't keep more than we have

    surviving: List[SwissPlayer] = []
    eliminated: List[SwissPlayer] = []

    for i, player in enumerate(ranked):
        if i < keep_count:
            surviving.append(player)
        elif player.total_battles < min_battles:
            # Not enough data to cut yet — protect them
            surviving.append(player)
        else:
            player.eliminated = True
            eliminated.append(player)

    return surviving, eliminated


# ── Reload ELOs from DB (after a round of parallel battles) ──────────────

async def reload_elos(players: List[SwissPlayer]) -> None:
    """
    Refresh each player's ELO and stats from the database.

    Called after each round so that the ELO values include the updates
    made by ``Leaderboard.record_battle()`` during parallel execution.
    """
    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        for player in players:
            db_entry = await repo.get_combatant(player.combatant_id)
            if db_entry:
                player.elo = db_entry.elo_rating
                player.total_battles = db_entry.total_battles
                player.wins = db_entry.wins
                player.losses = db_entry.losses


# ── Pretty print helpers ─────────────────────────────────────────────────

def print_standings(title: str, players: List[SwissPlayer], max_rows: int = 20) -> None:
    """Print a compact leaderboard for a list of players."""
    ranked = sorted(players, key=lambda p: p.elo, reverse=True)

    print(f"\n{'─' * 90}")
    print(f"  {title}")
    print(f"{'─' * 90}")
    print(f"  {'#':<4}{'Name':<42}{'ELO':>8}{'W':>5}{'L':>5}{'Tot':>5}{'Win%':>7}")
    print(f"  {'─' * 82}")

    for i, p in enumerate(ranked[:max_rows], 1):
        wr = (p.wins / p.total_battles * 100) if p.total_battles > 0 else 0
        name = p.display_name[:40]
        print(f"  {i:<4}{name:<42}{p.elo:>8.0f}{p.wins:>5}{p.losses:>5}{p.total_battles:>5}{wr:>6.1f}%")

    if len(ranked) > max_rows:
        print(f"  ... and {len(ranked) - max_rows} more")
    print(f"{'─' * 90}")


# ── Main tournament loop ─────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(description="Le Sésame Swiss Tournament")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K,
                        help=f"Number of top players to identify (default: {DEFAULT_TOP_K})")
    parser.add_argument("--rounds", type=int, default=DEFAULT_MAX_ROUNDS,
                        help=f"Maximum number of rounds (default: {DEFAULT_MAX_ROUNDS})")
    parser.add_argument("--battles-per-round", type=int, default=DEFAULT_BATTLES_PER_ROUND,
                        help=f"Battles each player plays per round (default: {DEFAULT_BATTLES_PER_ROUND})")
    parser.add_argument("--elimination-rate", type=float, default=DEFAULT_ELIMINATION_RATE,
                        help=f"Fraction eliminated each round (default: {DEFAULT_ELIMINATION_RATE})")
    parser.add_argument("--min-battles-before-cut", type=int, default=DEFAULT_MIN_BATTLES_BEFORE_CUT,
                        help=f"Min total battles before a player can be cut (default: {DEFAULT_MIN_BATTLES_BEFORE_CUT})")
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY,
                        help=f"Max parallel battles (default: {CONCURRENCY})")
    parser.add_argument("--no-elimination", action="store_true",
                        help="Disable elimination (pure Swiss, no cuts)")
    args = parser.parse_args()

    await init_db()

    # ── 1. Build the roster ──────────────────────────────────────────
    adversarials, guardians = await build_roster()

    total_advs = len(adversarials)
    total_guards = len(guardians)

    prior_advs = sum(1 for a in adversarials if a.total_battles > 0)
    prior_guards = sum(1 for g in guardians if g.total_battles > 0)

    print(f"\n{'═' * 90}")
    print(f"  LE SÉSAME ARENA — SWISS TOURNAMENT")
    print(f"{'═' * 90}")
    print(f"  Adversarials: {total_advs} ({prior_advs} with prior games)")
    print(f"  Guardians:    {total_guards} ({prior_guards} with prior games)")
    print(f"  Top-K:         {args.top_k}")
    print(f"  Max rounds:    {args.rounds}")
    print(f"  Battles/round: {args.battles_per_round}")
    print(f"  Elimination:   {'DISABLED' if args.no_elimination else f'{args.elimination_rate:.0%} per round (min {args.min_battles_before_cut} battles)'}")
    print(f"  Concurrency:   {args.concurrency}")
    print(f"{'═' * 90}\n")

    # ── 2. Load existing matchup set ─────────────────────────────────
    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        existing_matchups_raw = await repo.get_matchup_counts()
    existing_matchups: Set[Tuple[str, str]] = set(existing_matchups_raw.keys())

    active_advs = [a for a in adversarials if not a.eliminated]
    active_guards = [g for g in guardians if not g.eliminated]

    sem = asyncio.Semaphore(args.concurrency)
    total_battles_run = 0
    total_failures = 0

    for round_num in range(1, args.rounds + 1):
        print(f"\n{'▓' * 90}")
        print(f"  ROUND {round_num}/{args.rounds}  "
              f"| Active adversarials: {len(active_advs)}  "
              f"| Active guardians: {len(active_guards)}")
        print(f"{'▓' * 90}")

        # ── 2a. Check termination ────────────────────────────────────
        if len(active_advs) <= args.top_k and len(active_guards) <= args.top_k:
            print(f"  → Both pools are at or below top-{args.top_k}. Tournament complete.")
            break

        # ── 2b. Swiss pairing ────────────────────────────────────────
        pairings = swiss_pair(
            active_advs, active_guards,
            battles_per_round=args.battles_per_round,
            existing_matchups=existing_matchups,
        )

        if not pairings:
            print("  → No new pairings possible. All matchups exhausted.")
            break

        print(f"  Pairings this round: {len(pairings)}")

        # ── 2c. Execute battles in parallel ──────────────────────────
        tasks = []
        for i, (adv, guard) in enumerate(pairings, 1):
            label = (
                f"[{i}/{len(pairings)}] "
                f"{adv.display_name} vs {guard.display_name}"
            )
            task = asyncio.create_task(run_single_battle(sem, label, adv, guard))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        round_successes = sum(1 for ok, _ in results if ok)
        round_failures = sum(1 for ok, _ in results if not ok)
        total_battles_run += round_successes
        total_failures += round_failures

        print(f"\n  Round {round_num} results: {round_successes} OK, {round_failures} failed")

        # ── 2d. Reload ELOs from DB ──────────────────────────────────
        await reload_elos(active_advs)
        await reload_elos(active_guards)

        # ── 2e. Print interim standings ──────────────────────────────
        print_standings(
            f"ADVERSARIAL STANDINGS (round {round_num})", active_advs,
            max_rows=min(args.top_k + 5, len(active_advs)),
        )
        print_standings(
            f"GUARDIAN STANDINGS (round {round_num})", active_guards,
            max_rows=min(args.top_k + 5, len(active_guards)),
        )

        # ── 2f. Elimination ──────────────────────────────────────────
        if not args.no_elimination and round_num < args.rounds:
            active_advs, elim_advs = eliminate(
                active_advs, args.top_k, args.elimination_rate, args.min_battles_before_cut,
            )
            active_guards, elim_guards = eliminate(
                active_guards, args.top_k, args.elimination_rate, args.min_battles_before_cut,
            )
            if elim_advs or elim_guards:
                print(f"\n  ✂  Eliminated {len(elim_advs)} adversarials, {len(elim_guards)} guardians")
                if elim_advs:
                    bottom = sorted(elim_advs, key=lambda p: p.elo)
                    for p in bottom[:5]:
                        print(f"     ↓ {p.display_name} (ELO {p.elo:.0f}, {p.total_battles} games)")
                    if len(bottom) > 5:
                        print(f"     ... and {len(bottom) - 5} more")
                if elim_guards:
                    bottom = sorted(elim_guards, key=lambda p: p.elo)
                    for p in bottom[:5]:
                        print(f"     ↓ {p.display_name} (ELO {p.elo:.0f}, {p.total_battles} games)")
                    if len(bottom) > 5:
                        print(f"     ... and {len(bottom) - 5} more")

    # ── Final results ────────────────────────────────────────────────
    print(f"\n{'═' * 90}")
    print(f"  TOURNAMENT COMPLETE")
    print(f"  Battles run: {total_battles_run}  |  Failures: {total_failures}")
    print(f"{'═' * 90}")

    print_standings(f"FINAL TOP-{args.top_k} ADVERSARIALS", active_advs, max_rows=args.top_k)
    print_standings(f"FINAL TOP-{args.top_k} GUARDIANS", active_guards, max_rows=args.top_k)

    # Also show the official DB leaderboard
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))
        print(await leaderboard.display_rankings(CombatantType.GUARDIAN))


if __name__ == "__main__":
    asyncio.run(main())
