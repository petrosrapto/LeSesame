"""
Register new players into an existing leaderboard without rerunning the
full Swiss tournament.

Instead of replaying ~10,000 battles, this script inserts individual
combatants by running a small, targeted set of battles against the
existing opponent pool.

Algorithm — two-phase online insertion
──────────────────────────────────────
  Phase 1 — Calibration (stratified sampling):
      Divide existing opponents into ELO-percentile brackets, sample a
      few from each, and run battles.  This quickly moves the new
      player from the default 1500 toward their true ELO by testing
      them against the full skill spectrum.

  Phase 2 — Refinement (ELO-proximity pairing):
      After calibration, repeatedly pair the new player against the
      closest-ELO opponent they haven't played yet.  Run in small
      batches (default 3), reloading ELO after each batch so the next
      pairing reflects the latest rating.  This sharpens the estimate
      at the decision boundary.

Total default: 15 calibration + 10 refinement = 25 battles per player.

Usage (inside the backend container):
    # Register a single new combatant
    python -m scripts.arena.online_registration \\
        --type adversarial --level 3 \\
        --model-id gpt-5 --provider openai

    # Register all default levels for a new model (both types)
    python -m scripts.arena.online_registration \\
        --model-id gpt-5 --provider openai

    # Register specific levels, adversarial only
    python -m scripts.arena.online_registration \\
        --type adversarial --levels 1 3 5 \\
        --model-id gpt-5 --provider openai

    # Custom battle budget
    python -m scripts.arena.online_registration \\
        --model-id gpt-5 --provider openai \\
        --calibration-battles 20 --refinement-battles 15

    # OpenAI-compatible endpoint
    python -m scripts.arena.online_registration \\
        --model-id deepseek-chat --provider openai \\
        --endpoint-url https://api.deepseek.com

Author: Petros Raptopoulos
Date: 2026/02/11
"""

import argparse
import asyncio
import random
import traceback
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set, Tuple

from app.services.arena.engine import ArenaEngine, GUARDIAN_INFO
from app.services.arena.models import BattleConfig, CombatantType
from app.services.arena.leaderboard import Leaderboard
from app.services.adversarials.factory import ADVERSARIAL_INFO
from app.db.database import async_session_maker, init_db
from app.db.repositories.arena_repository import ArenaRepository

from scripts.arena.swiss_tournament import (
    MODELS,
    MODEL_LOOKUP,
    MAX_TURNS,
    MAX_GUESSES,
    SwissPlayer,
    build_model_config,
    _model_info,
    run_single_battle,
    reload_elos,
    print_standings,
)


# ── Default parameters ───────────────────────────────────────────────────

DEFAULT_CALIBRATION_BATTLES = 15    # 5 brackets × 3 battles
DEFAULT_REFINEMENT_BATTLES = 10
DEFAULT_NUM_BRACKETS = 5
DEFAULT_BATTLES_PER_BRACKET = 3
DEFAULT_REFINEMENT_BATCH_SIZE = 3
DEFAULT_CONCURRENCY = 5
DEFAULT_ADV_LEVELS = [1, 2, 3, 4, 5]
DEFAULT_GUARD_LEVELS = [1, 2, 3, 4, 5]


# ── Opponent loading ─────────────────────────────────────────────────────

async def load_existing_opponents(
    opponent_type: str,
) -> List[SwissPlayer]:
    """
    Load all existing combatants of the given type from the database and
    convert them to SwissPlayer objects (with model config details looked
    up from the MODELS list).

    Only returns players that have at least 1 battle (i.e. established
    ELO) so that calibration opponents are meaningful.

    Args:
        opponent_type: ``"guardian"`` or ``"adversarial"``.

    Returns:
        List of SwissPlayer objects with ELO, stats, and model config.
    """
    players: List[SwissPlayer] = []

    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        db_entries = await repo.get_rankings(combatant_type=opponent_type)

    for entry in db_entries:
        # Only include players with battle history (stable ELO)
        if entry.total_battles == 0:
            continue

        # Look up provider/endpoint from the MODELS list
        model_tuple = MODEL_LOOKUP.get(entry.model_id)
        if model_tuple:
            display_name, _, provider, endpoint_url = model_tuple
        else:
            # Unknown model — skip (we can't build a model_config for it)
            continue

        type_prefix = "Guard" if opponent_type == "guardian" else "Adv"
        player = SwissPlayer(
            combatant_id=entry.combatant_id,
            combatant_type=opponent_type,
            level=entry.level,
            model_id=entry.model_id,
            display_name=f"{type_prefix} L{entry.level} [{display_name}]",
            provider=provider,
            endpoint_url=endpoint_url,
            elo=entry.elo_rating,
            total_battles=entry.total_battles,
            wins=entry.wins,
            losses=entry.losses,
        )
        players.append(player)

    return players


# ── Stratified sampling ──────────────────────────────────────────────────

def stratify_opponents(
    opponents: List[SwissPlayer],
    num_brackets: int = DEFAULT_NUM_BRACKETS,
) -> List[List[SwissPlayer]]:
    """
    Divide opponents into ELO-percentile brackets.

    The opponents are sorted by ELO descending and split into
    ``num_brackets`` roughly equal groups.  This ensures calibration
    covers the full skill spectrum.

    Returns:
        List of brackets, each a list of SwissPlayer.  Index 0 is the
        strongest bracket.
    """
    sorted_opps = sorted(opponents, key=lambda p: p.elo, reverse=True)
    if not sorted_opps:
        return []

    bracket_size = max(1, len(sorted_opps) // num_brackets)
    brackets: List[List[SwissPlayer]] = []
    for i in range(num_brackets):
        start = i * bracket_size
        end = start + bracket_size if i < num_brackets - 1 else len(sorted_opps)
        if start < len(sorted_opps):
            brackets.append(sorted_opps[start:end])

    return brackets


def select_calibration_opponents(
    new_player_id: str,
    opponents: List[SwissPlayer],
    num_brackets: int = DEFAULT_NUM_BRACKETS,
    battles_per_bracket: int = DEFAULT_BATTLES_PER_BRACKET,
    existing_matchups: Optional[Set[Tuple[str, str]]] = None,
) -> List[SwissPlayer]:
    """
    Select opponents for the calibration phase via stratified sampling.

    From each ELO-percentile bracket, samples ``battles_per_bracket``
    opponents that the new player has not yet faced.  Falls back to
    already-played opponents if unplayed ones are exhausted within a
    bracket.

    Returns:
        Ordered list of opponents to fight during calibration.
    """
    if existing_matchups is None:
        existing_matchups = set()

    brackets = stratify_opponents(opponents, num_brackets)
    selected: List[SwissPlayer] = []

    for bracket in brackets:
        # Prefer opponents not yet played
        unplayed = [
            o for o in bracket
            if (new_player_id, o.combatant_id) not in existing_matchups
            and (o.combatant_id, new_player_id) not in existing_matchups
        ]
        pool = unplayed if len(unplayed) >= battles_per_bracket else bracket
        sampled = random.sample(pool, min(battles_per_bracket, len(pool)))
        selected.extend(sampled)

    return selected


def select_refinement_opponents(
    new_player: SwissPlayer,
    all_opponents: List[SwissPlayer],
    num_battles: int,
    played_ids: Set[str],
) -> List[SwissPlayer]:
    """
    Select closest-ELO opponents not yet played for the refinement phase.

    If all opponents have been played, allows rematches sorted by ELO
    proximity to the new player's current rating.

    Returns:
        List of opponents for the next refinement batch.
    """
    unplayed = [o for o in all_opponents if o.combatant_id not in played_ids]
    pool = unplayed if unplayed else all_opponents

    # Sort by ELO distance from new player (closest first)
    pool_sorted = sorted(pool, key=lambda o: abs(o.elo - new_player.elo))
    return pool_sorted[:num_battles]


# ── Battle execution helpers ─────────────────────────────────────────────

async def run_battles_for_player(
    new_player: SwissPlayer,
    opponents: List[SwissPlayer],
    sem: asyncio.Semaphore,
    phase_label: str,
    battle_offset: int = 0,
) -> Tuple[int, int]:
    """
    Run battles between a new player and a list of opponents.

    Args:
        new_player: The new combatant being registered.
        opponents: Opponents to fight.
        sem: Concurrency semaphore.
        phase_label: Label prefix for output (e.g. "Cal" or "Ref").
        battle_offset: Starting index for labeling.

    Returns:
        (successes, failures)
    """
    tasks = []
    for i, opponent in enumerate(opponents, battle_offset + 1):
        if new_player.combatant_type == "adversarial":
            adv, guard = new_player, opponent
        else:
            adv, guard = opponent, new_player

        label = (
            f"[{phase_label} {i}] "
            f"{adv.display_name} vs {guard.display_name}"
        )
        task = asyncio.create_task(run_single_battle(sem, label, adv, guard))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    successes = sum(1 for ok, _ in results if ok)
    failures = sum(1 for ok, _ in results if not ok)
    return successes, failures


# ── Core: online insertion of a single player ────────────────────────────

async def insert_player_online(
    new_player: SwissPlayer,
    all_opponents: List[SwissPlayer],
    calibration_battles: int = DEFAULT_CALIBRATION_BATTLES,
    refinement_battles: int = DEFAULT_REFINEMENT_BATTLES,
    num_brackets: int = DEFAULT_NUM_BRACKETS,
    refinement_batch_size: int = DEFAULT_REFINEMENT_BATCH_SIZE,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> Tuple[float, int]:
    """
    Insert a single new player into the existing leaderboard using a
    two-phase online approach.

    Phase 1 — Calibration:
        Stratified sampling across ELO brackets.  All calibration battles
        run in parallel.

    Phase 2 — Refinement:
        ELO-proximity pairing in small sequential batches.  After each
        batch, the player's ELO is reloaded from the DB so that the next
        batch pairs against the right opponents.

    Args:
        new_player: The new combatant to insert.
        all_opponents: Full list of existing opponents (opposite type).
        calibration_battles: Total battles in the calibration phase.
        refinement_battles: Total battles in the refinement phase.
        num_brackets: Number of ELO brackets for stratified sampling.
        refinement_batch_size: Battles per refinement batch before
            reloading ELO.
        concurrency: Max parallel battles.

    Returns:
        (final_elo, total_battles_played)
    """
    if not all_opponents:
        print(f"    No opponents available for {new_player.display_name}. Skipping.")
        return new_player.elo, 0

    sem = asyncio.Semaphore(concurrency)
    played_ids: Set[str] = set()
    total_ok = 0
    total_fail = 0

    # Load existing matchups for this player
    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        existing_matchups_raw = await repo.get_matchup_counts()
    existing_matchups: Set[Tuple[str, str]] = set(existing_matchups_raw.keys())

    # ── Phase 1: Calibration (stratified sampling) ────────────────
    battles_per_bracket = max(1, calibration_battles // num_brackets)
    cal_opponents = select_calibration_opponents(
        new_player_id=new_player.combatant_id,
        opponents=all_opponents,
        num_brackets=num_brackets,
        battles_per_bracket=battles_per_bracket,
        existing_matchups=existing_matchups,
    )

    if cal_opponents:
        print(f"\n  Phase 1 — Calibration: {len(cal_opponents)} battles "
              f"({num_brackets} brackets × {battles_per_bracket} each)")

        ok, fail = await run_battles_for_player(
            new_player, cal_opponents, sem, "Cal",
        )
        total_ok += ok
        total_fail += fail

        # Track who we played
        for opp in cal_opponents:
            played_ids.add(opp.combatant_id)

        # Reload ELO after calibration
        await reload_elos([new_player])
        print(f"    Calibration complete: {ok} OK, {fail} failed "
              f"→ ELO {new_player.elo:.0f}")

    # ── Phase 2: Refinement (ELO-proximity batches) ───────────────
    remaining = refinement_battles
    ref_total_ok = 0
    ref_total_fail = 0
    batch_num = 0

    print(f"\n  Phase 2 — Refinement: up to {refinement_battles} battles "
          f"(batches of {refinement_batch_size})")

    while remaining > 0:
        batch_num += 1
        batch_count = min(refinement_batch_size, remaining)

        # Select closest-ELO opponents
        ref_opponents = select_refinement_opponents(
            new_player, all_opponents, batch_count, played_ids,
        )
        if not ref_opponents:
            print("    No more opponents available for refinement.")
            break

        ok, fail = await run_battles_for_player(
            new_player, ref_opponents, sem, f"Ref-B{batch_num}",
            battle_offset=ref_total_ok + ref_total_fail,
        )
        ref_total_ok += ok
        ref_total_fail += fail

        for opp in ref_opponents:
            played_ids.add(opp.combatant_id)

        # Reload ELO after each batch
        await reload_elos([new_player])
        remaining -= len(ref_opponents)

        print(f"    Batch {batch_num}: {ok} OK, {fail} failed "
              f"→ ELO {new_player.elo:.0f}")

    total_ok += ref_total_ok
    total_fail += ref_total_fail

    print(f"\n  Done: {total_ok} battles played ({total_fail} failed) "
          f"→ final ELO {new_player.elo:.0f}")

    return new_player.elo, total_ok


# ── Build new player roster ──────────────────────────────────────────────

async def build_new_players(
    model_id: str,
    provider: str,
    endpoint_url: Optional[str],
    player_type: Optional[str],
    levels: Optional[List[int]],
) -> Tuple[List[SwissPlayer], List[SwissPlayer]]:
    """
    Build SwissPlayer objects for the new combatants to register and
    ensure they exist in the database (with guardian validation).

    Args:
        model_id: LLM model identifier.
        provider: LLM provider (e.g. "openai", "anthropic").
        endpoint_url: Optional custom API endpoint.
        player_type: ``"adversarial"``, ``"guardian"``, or None for both.
        levels: List of levels to register, or None for defaults.

    Returns:
        (new_adversarials, new_guardians) — SwissPlayers ready for
        online insertion.
    """
    adv_levels = levels if levels else DEFAULT_ADV_LEVELS
    guard_levels = levels if levels else DEFAULT_GUARD_LEVELS

    new_advs: List[SwissPlayer] = []
    new_guards: List[SwissPlayer] = []

    model_config = build_model_config(model_id, provider, endpoint_url)

    # Determine display name
    model_tuple = MODEL_LOOKUP.get(model_id)
    display_name = model_tuple[0] if model_tuple else model_id

    async with async_session_maker() as session:
        repo = ArenaRepository(session)
        leaderboard = Leaderboard(session)

        # ── Adversarials ──
        if player_type in (None, "adversarial"):
            for level in adv_levels:
                cid = f"adversarial_L{level}_{model_id}"
                db_entry = await repo.get_combatant(cid)

                # Skip if already has battles (already registered)
                if db_entry and db_entry.total_battles > 0:
                    print(f"  {cid} already has {db_entry.total_battles} battles "
                          f"(ELO {db_entry.elo_rating:.0f}) — skipping.")
                    continue

                # Ensure DB row exists
                if not db_entry:
                    a_info = ADVERSARIAL_INFO.get(
                        level, {"name": "Unknown", "title": "Unknown"},
                    )
                    db_entry = await repo.upsert_combatant(
                        combatant_id=cid,
                        combatant_type="adversarial",
                        level=level,
                        name=a_info["name"],
                        title=a_info["title"],
                        model_id=model_id,
                    )
                    await session.commit()

                player = SwissPlayer(
                    combatant_id=cid,
                    combatant_type="adversarial",
                    level=level,
                    model_id=model_id,
                    display_name=f"Adv L{level} [{display_name}]",
                    provider=provider,
                    endpoint_url=endpoint_url,
                    elo=db_entry.elo_rating if db_entry else 1500.0,
                    total_battles=db_entry.total_battles if db_entry else 0,
                )
                new_advs.append(player)

        # ── Guardians (with validation) ──
        if player_type in (None, "guardian"):
            for level in guard_levels:
                cid = f"guardian_L{level}_{model_id}"
                db_entry = await repo.get_combatant(cid)

                # Skip if already has battles
                if db_entry and db_entry.total_battles > 0:
                    print(f"  {cid} already has {db_entry.total_battles} battles "
                          f"(ELO {db_entry.elo_rating:.0f}) — skipping.")
                    continue

                # Ensure DB row exists
                if not db_entry:
                    g_info = GUARDIAN_INFO.get(
                        level, {"name": "Unknown", "title": "Unknown"},
                    )
                    db_entry = await repo.upsert_combatant(
                        combatant_id=cid,
                        combatant_type="guardian",
                        level=level,
                        name=g_info["name"],
                        title=g_info["title"],
                        model_id=model_id,
                    )
                    await session.commit()

                # Validate guardian
                guardian_ok = await leaderboard.ensure_guardian_validated(
                    combatant_id=cid,
                    level=level,
                    model_config=model_config,
                )
                await session.commit()

                if not guardian_ok:
                    print(f"  Guardian L{level} [{display_name}] "
                          f"FAILED validation — excluded.")
                    continue

                player = SwissPlayer(
                    combatant_id=cid,
                    combatant_type="guardian",
                    level=level,
                    model_id=model_id,
                    display_name=f"Guard L{level} [{display_name}]",
                    provider=provider,
                    endpoint_url=endpoint_url,
                    elo=db_entry.elo_rating if db_entry else 1500.0,
                    total_battles=db_entry.total_battles if db_entry else 0,
                )
                new_guards.append(player)

    return new_advs, new_guards


# ── Main ─────────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register new players into an existing leaderboard "
                    "without rerunning the full Swiss tournament.",
    )

    # Required: model identification
    parser.add_argument(
        "--model-id", required=True,
        help="LLM model identifier (e.g. 'gpt-5', 'claude-opus-4-6')",
    )
    parser.add_argument(
        "--provider", required=True,
        help="LLM provider (e.g. 'openai', 'anthropic', 'mistral', 'google')",
    )
    parser.add_argument(
        "--endpoint-url", default=None,
        help="Custom API endpoint URL (for OpenAI-compatible providers)",
    )

    # Optional: scope
    parser.add_argument(
        "--type", choices=["adversarial", "guardian"], default=None,
        help="Register only adversarials or only guardians "
             "(default: both)",
    )
    parser.add_argument(
        "--levels", type=int, nargs="+", default=None,
        help="Specific levels to register (default: 1-5)",
    )

    # Optional: battle budget
    parser.add_argument(
        "--calibration-battles", type=int,
        default=DEFAULT_CALIBRATION_BATTLES,
        help=f"Battles in calibration phase per player "
             f"(default: {DEFAULT_CALIBRATION_BATTLES})",
    )
    parser.add_argument(
        "--refinement-battles", type=int,
        default=DEFAULT_REFINEMENT_BATTLES,
        help=f"Battles in refinement phase per player "
             f"(default: {DEFAULT_REFINEMENT_BATTLES})",
    )
    parser.add_argument(
        "--num-brackets", type=int,
        default=DEFAULT_NUM_BRACKETS,
        help=f"Number of ELO brackets for calibration "
             f"(default: {DEFAULT_NUM_BRACKETS})",
    )
    parser.add_argument(
        "--concurrency", type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Max parallel battles (default: {DEFAULT_CONCURRENCY})",
    )

    args = parser.parse_args()

    await init_db()

    total_battles = args.calibration_battles + args.refinement_battles

    # ── 1. Build new player roster ────────────────────────────────
    print(f"\n{'=' * 90}")
    print(f"  LE SESAME ARENA — ONLINE PLAYER REGISTRATION")
    print(f"{'=' * 90}")
    print(f"  Model:       {args.model_id} ({args.provider})")
    if args.endpoint_url:
        print(f"  Endpoint:    {args.endpoint_url}")
    print(f"  Type:        {args.type or 'both (adversarial + guardian)'}")
    print(f"  Levels:      {args.levels or 'default (1-5)'}")
    print(f"  Budget:      {total_battles} battles/player "
          f"({args.calibration_battles} calibration + "
          f"{args.refinement_battles} refinement)")
    print(f"  Concurrency: {args.concurrency}")
    print(f"{'=' * 90}\n")

    print("Building new player roster...")
    new_advs, new_guards = await build_new_players(
        model_id=args.model_id,
        provider=args.provider,
        endpoint_url=args.endpoint_url,
        player_type=args.type,
        levels=args.levels,
    )

    total_new = len(new_advs) + len(new_guards)
    if total_new == 0:
        print("\nNo new players to register. All requested combatants "
              "already have battle history.")
        return

    print(f"\n  New adversarials: {len(new_advs)}")
    print(f"  New guardians:    {len(new_guards)}")
    print(f"  Estimated total battles: ~{total_new * total_battles}")

    # ── 2. Load existing opponents ────────────────────────────────
    print("\nLoading existing opponents from database...")

    existing_guardians: List[SwissPlayer] = []
    existing_adversarials: List[SwissPlayer] = []

    if new_advs:
        existing_guardians = await load_existing_opponents("guardian")
        print(f"  Available guardian opponents: {len(existing_guardians)}")

    if new_guards:
        existing_adversarials = await load_existing_opponents("adversarial")
        print(f"  Available adversarial opponents: {len(existing_adversarials)}")

    # ── 3. Register each new player ───────────────────────────────
    grand_total_ok = 0
    grand_total_fail = 0

    # Process adversarials first
    for i, player in enumerate(new_advs, 1):
        print(f"\n{'▓' * 90}")
        print(f"  REGISTERING [{i}/{total_new}]: {player.display_name}")
        print(f"{'▓' * 90}")

        elo, battles = await insert_player_online(
            new_player=player,
            all_opponents=existing_guardians,
            calibration_battles=args.calibration_battles,
            refinement_battles=args.refinement_battles,
            num_brackets=args.num_brackets,
            concurrency=args.concurrency,
        )
        grand_total_ok += battles

    # Process guardians
    for i, player in enumerate(new_guards, len(new_advs) + 1):
        print(f"\n{'▓' * 90}")
        print(f"  REGISTERING [{i}/{total_new}]: {player.display_name}")
        print(f"{'▓' * 90}")

        elo, battles = await insert_player_online(
            new_player=player,
            all_opponents=existing_adversarials,
            calibration_battles=args.calibration_battles,
            refinement_battles=args.refinement_battles,
            num_brackets=args.num_brackets,
            concurrency=args.concurrency,
        )
        grand_total_ok += battles

    # ── 4. Final results ──────────────────────────────────────────
    print(f"\n{'=' * 90}")
    print(f"  REGISTRATION COMPLETE")
    print(f"  Total battles: {grand_total_ok}")
    print(f"{'=' * 90}")

    # Reload all new players for final standings
    all_new = new_advs + new_guards
    await reload_elos(all_new)

    if new_advs:
        print_standings("NEW ADVERSARIALS — FINAL RATINGS", new_advs,
                        max_rows=len(new_advs))
    if new_guards:
        print_standings("NEW GUARDIANS — FINAL RATINGS", new_guards,
                        max_rows=len(new_guards))

    # Show where new players rank in the overall leaderboard
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        if new_advs:
            print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))
        if new_guards:
            print(await leaderboard.display_rankings(CombatantType.GUARDIAN))


if __name__ == "__main__":
    asyncio.run(main())
