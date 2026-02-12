"""
Le Sésame Backend - Arena CLI Runner

Command-line interface for running battles between adversarials
and guardians, and viewing leaderboard results.

Usage:
    # Single battle: adversarial L3 vs guardian L2
    python -m app.services.arena.runner battle --adv 3 --guard 2

    # Run a full tournament (all adversarials vs all guardians)
    python -m app.services.arena.runner tournament

    # Show leaderboard
    python -m app.services.arena.runner leaderboard

    # Show leaderboard for specific type
    python -m app.services.arena.runner leaderboard --type adversarial
    python -m app.services.arena.runner leaderboard --type guardian

    # Reset leaderboard
    python -m app.services.arena.runner reset

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import argparse
import asyncio
import sys
from typing import Dict, Any, List, Optional

from .engine import ArenaEngine
from .models import BattleConfig, CombatantType
from .leaderboard import Leaderboard
from ...db.database import async_session_maker, init_db


# ANSI color codes for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


async def progress_callback(event: str, data: Dict[str, Any]) -> None:
    """Print battle progress to terminal with colors."""
    if event == "battle_start":
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}  ⚔️  ARENA BATTLE  ⚔️{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"  {Colors.BLUE}Guardian:{Colors.RESET}    {data['guardian']}")
        print(f"  {Colors.RED}Adversarial:{Colors.RESET} {data['adversarial']}")
        print(f"  {Colors.DIM}Max turns: {data['max_turns']} | Max guesses: {data['max_guesses']}{Colors.RESET}")
        print(f"{Colors.BOLD}{'─' * 70}{Colors.RESET}\n")

    elif event == "adversarial_turn":
        turn = data["turn"]
        msg = data["message"]
        print(f"  {Colors.RED}◆ [Turn {turn}] Adversarial:{Colors.RESET}")
        # Indent and wrap message
        for line in msg.split("\n"):
            print(f"    {Colors.RED}{line}{Colors.RESET}")
        print()

    elif event == "guardian_turn":
        turn = data["turn"]
        resp = data["response"]
        leaked = data.get("leaked", False)
        color = Colors.YELLOW if leaked else Colors.BLUE
        leak_marker = f" {Colors.BOLD}⚠️  SECRET LEAKED!{Colors.RESET}" if leaked else ""
        print(f"  {color}◇ [Turn {turn}] Guardian:{leak_marker}{Colors.RESET}")
        for line in resp.split("\n"):
            print(f"    {color}{line}{Colors.RESET}")
        print()

    elif event == "secret_leaked":
        print(f"  {Colors.YELLOW}⚠️  Leak detected at round {data['round']} (informational — battle continues){Colors.RESET}\n")

    elif event == "guess":
        gn = data["guess_number"]
        guess = data["guess"]
        correct = data["correct"]
        remaining = data.get("guesses_remaining", "?")
        if correct:
            print(f"  {Colors.GREEN}✓ Guess #{gn}: {guess} — CORRECT!{Colors.RESET}")
        else:
            print(f"  {Colors.DIM}✗ Guess #{gn}: {guess} — Wrong ({remaining} remaining){Colors.RESET}")

    elif event == "battle_end":
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        outcome = data["outcome"]
        if data["adversarial_won"]:
            print(f"  {Colors.RED}{Colors.BOLD}🏆 ADVERSARIAL WINS — {outcome}{Colors.RESET}")
        else:
            print(f"  {Colors.BLUE}{Colors.BOLD}🛡️  GUARDIAN WINS — Secret protected{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}")


async def run_battle(
    adv_level: int,
    guard_level: int,
    max_turns: int = 10,
    max_guesses: int = 3,
    adv_model_config: Optional[Dict[str, Any]] = None,
    guard_model_config: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> None:
    """Run a single battle and record results."""
    config = BattleConfig(
        guardian_level=guard_level,
        adversarial_level=adv_level,
        max_turns=max_turns,
        max_guesses=max_guesses,
        adversarial_model_config=adv_model_config,
        guardian_model_config=guard_model_config,
    )

    engine = ArenaEngine(config)
    callback = progress_callback if verbose else None

    # Validate the guardian before allowing it to battle
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        # Ensure combatant exists in DB before validating
        await leaderboard.ensure_combatants(
            model_id=engine.guardian_combatant.model_id,
        )
        await session.commit()

        guardian_ok = await leaderboard.ensure_guardian_validated(
            combatant_id=engine.guardian_combatant.combatant_id,
            level=guard_level,
            model_config=guard_model_config,
        )
        await session.commit()

        if not guardian_ok:
            print(
                f"\n{Colors.YELLOW}Guardian L{guard_level} "
                f"[{engine.guardian_combatant.model_id}] FAILED validation "
                f"— skipping battle.{Colors.RESET}"
            )
            return

    result = await engine.run_battle(on_progress=callback)

    # Record in leaderboard (DB) — combatants are auto-registered
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        result = await leaderboard.record_battle(result)
        await session.commit()

    # Print summary
    print(f"\n{result.summary()}")
    print(f"\n{Colors.DIM}Actual secret: {result.actual_secret}{Colors.RESET}")


async def run_tournament(
    max_turns: int = 10,
    max_guesses: int = 3,
    rounds_per_matchup: int = 3,
    adv_levels: Optional[List[int]] = None,
    guard_levels: Optional[List[int]] = None,
    adv_model: Optional[str] = None,
    guard_model: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """
    Run a tournament.

    Supports incremental execution: only matchups that haven't yet
    reached ``rounds_per_matchup`` are played.  You can restrict the
    grid to a subset of levels with ``--adv`` / ``--guard`` and
    specify LLM models with ``--adv-model`` / ``--guard-model``.
    """
    from ...core import settings

    adv_range = adv_levels or list(range(1, 21))
    guard_range = guard_levels or list(range(1, 21))

    adv_model_config = {"model_id": adv_model} if adv_model else None
    guard_model_config = {"model_id": guard_model} if guard_model else None

    # Resolve effective model_id for combatant_id construction
    eff_adv_model = adv_model or settings.llm_model
    eff_guard_model = guard_model or settings.llm_model

    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)

        # Query how many rounds each matchup already has
        matchup_counts = await leaderboard.repo.get_matchup_counts()

        # Build the work list: only matchups that need more rounds
        work: list[tuple[int, int, int]] = []  # (adv_level, guard_level, rounds_needed)
        for adv_level in adv_range:
            for guard_level in guard_range:
                key = (
                    f"adversarial_L{adv_level}_{eff_adv_model}",
                    f"guardian_L{guard_level}_{eff_guard_model}",
                )
                already_done = matchup_counts.get(key, 0)
                remaining = max(0, rounds_per_matchup - already_done)
                if remaining > 0:
                    work.append((adv_level, guard_level, remaining))

        total_battles = sum(r for _, _, r in work)

        if total_battles == 0:
            print(f"\n{Colors.GREEN}All matchups already have {rounds_per_matchup} rounds. Nothing to do.{Colors.RESET}")
            print(await leaderboard.display_rankings(CombatantType.GUARDIAN))
            print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))
            return

        # Header
        total_matchups = len(adv_range) * len(guard_range)
        skipped = total_matchups - len(work)
        print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}  🏟️  LE SÉSAME ARENA TOURNAMENT  🏟️{Colors.RESET}")
        print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}")
        print(f"  Grid: {len(adv_range)} adversarials × {len(guard_range)} guardians = {total_matchups} matchups")
        print(f"  Adversarial model: {eff_adv_model} | Guardian model: {eff_guard_model}")
        print(f"  Target rounds per matchup: {rounds_per_matchup}")
        if skipped:
            print(f"  {Colors.DIM}Skipping {skipped} matchups already at target{Colors.RESET}")
        print(f"  Battles to run: {total_battles}")
        print(f"  Max turns: {max_turns} | Max guesses: {max_guesses}")
        print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}\n")

        # Pre-validate guardians so failed ones are excluded from the work list
        validated_guardians: dict[int, bool] = {}  # guard_level → passed
        for _, guard_level, _ in work:
            if guard_level not in validated_guardians:
                guard_cid = f"guardian_L{guard_level}_{eff_guard_model}"
                await leaderboard.ensure_combatants(model_id=eff_guard_model)
                await session.commit()
                passed = await leaderboard.ensure_guardian_validated(
                    combatant_id=guard_cid,
                    level=guard_level,
                    model_config=guard_model_config,
                )
                await session.commit()
                validated_guardians[guard_level] = passed
                if not passed:
                    print(
                        f"  {Colors.YELLOW}Guardian L{guard_level} [{eff_guard_model}] "
                        f"FAILED validation — excluding from tournament.{Colors.RESET}"
                    )

        # Filter out matchups with failed guardians
        work = [(a, g, r) for a, g, r in work if validated_guardians.get(g, False)]
        total_battles = sum(r for _, _, r in work)

        if total_battles == 0:
            print(f"\n{Colors.YELLOW}No valid matchups remaining after guardian validation.{Colors.RESET}")
            print(await leaderboard.display_rankings(CombatantType.GUARDIAN))
            print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))
            return

        current = 0
        for adv_level, guard_level, rounds_needed in work:
            for round_num in range(rounds_needed):
                current += 1
                config = BattleConfig(
                    guardian_level=guard_level,
                    adversarial_level=adv_level,
                    max_turns=max_turns,
                    max_guesses=max_guesses,
                    adversarial_model_config=adv_model_config,
                    guardian_model_config=guard_model_config,
                )

                engine = ArenaEngine(config)
                callback = progress_callback if verbose else None

                print(
                    f"  [{current}/{total_battles}] "
                    f"Adv L{adv_level} [{eff_adv_model}] vs Guard L{guard_level} [{eff_guard_model}]"
                    f"{f' (round {round_num + 1}/{rounds_needed})' if rounds_needed > 1 else ''} ... ",
                    end="",
                    flush=True,
                )

                try:
                    result = await engine.run_battle(on_progress=callback)
                    result = await leaderboard.record_battle(result)
                    await session.commit()

                    if result.adversarial_won:
                        print(f"{Colors.RED}Adversarial wins ({result.outcome.value}){Colors.RESET}")
                    else:
                        print(f"{Colors.BLUE}Guardian wins{Colors.RESET}")

                except Exception as e:
                    await session.rollback()
                    print(f"{Colors.YELLOW}Error: {e}{Colors.RESET}")

        # Show final leaderboard
        print(await leaderboard.display_rankings(CombatantType.GUARDIAN))
        print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))


async def seed_combatants(model_id: Optional[str] = None) -> None:
    """Register all known combatants in the database without running any battles."""
    from ...core import settings

    effective_model = model_id or settings.llm_model
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        await leaderboard.ensure_combatants(model_id=effective_model)
        await session.commit()
    print(f"{Colors.GREEN}All combatants seeded for model '{effective_model}'.{Colors.RESET}")


async def show_leaderboard(combatant_type: Optional[str] = None) -> None:
    """Display the current leaderboard."""
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        if combatant_type:
            ct = CombatantType(combatant_type)
            print(await leaderboard.display_rankings(ct))
        else:
            print(await leaderboard.display_rankings(CombatantType.GUARDIAN))
            print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))


async def reset_leaderboard() -> None:
    """Reset the leaderboard."""
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        await leaderboard.reset()
        await session.commit()
    print(f"{Colors.GREEN}Leaderboard has been reset.{Colors.RESET}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Le Sésame Arena — Adversarial vs Guardian Battles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single battle
  python -m app.services.arena.runner battle --adv 3 --guard 2

  # Battle with specific LLM models
  python -m app.services.arena.runner battle --adv 3 --guard 2 --adv-model gpt-4o --guard-model mistral-small-latest

  # Run a full tournament (incremental — skips completed matchups)
  python -m app.services.arena.runner tournament

  # Tournament with specific models
  python -m app.services.arena.runner tournament --adv-model gpt-4o --guard-model gpt-4o

  # Run tournament for a specific adversarial against all guardians
  python -m app.services.arena.runner tournament --adv 3

  # Run tournament for specific adversarials vs specific guardians
  python -m app.services.arena.runner tournament --adv 1 3 5 --guard 2 4

  # Add 2 more rounds to each matchup (tops up to 5 total)
  python -m app.services.arena.runner tournament --rounds 5

  # Seed all combatants for a specific model
  python -m app.services.arena.runner seed --model gpt-4o

  # Show leaderboard
  python -m app.services.arena.runner leaderboard

  # Reset leaderboard
  python -m app.services.arena.runner reset
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Battle command
    battle_parser = subparsers.add_parser("battle", help="Run a single battle")
    battle_parser.add_argument("--adv", type=int, required=True, help="Adversarial level (1-5)")
    battle_parser.add_argument("--guard", type=int, required=True, help="Guardian level (1-5)")
    battle_parser.add_argument("--adv-model", type=str, default=None, help="LLM model for adversarial (default: config)")
    battle_parser.add_argument("--guard-model", type=str, default=None, help="LLM model for guardian (default: config)")
    battle_parser.add_argument("--turns", type=int, default=10, help="Max conversation turns (default: 10)")
    battle_parser.add_argument("--guesses", type=int, default=3, help="Max secret guesses (default: 3)")
    battle_parser.add_argument("--quiet", action="store_true", help="Suppress turn-by-turn output")

    # Tournament command (incremental by default)
    tournament_parser = subparsers.add_parser(
        "tournament",
        help="Run a tournament (incremental — only plays missing rounds)",
    )
    tournament_parser.add_argument("--turns", type=int, default=10, help="Max conversation turns (default: 10)")
    tournament_parser.add_argument("--guesses", type=int, default=3, help="Max secret guesses (default: 3)")
    tournament_parser.add_argument("--rounds", type=int, default=3, help="Target rounds per matchup (default: 3)")
    tournament_parser.add_argument(
        "--adv", type=int, nargs="+", default=None,
        help="Adversarial levels to include (default: all 1-5). Example: --adv 1 3 5",
    )
    tournament_parser.add_argument(
        "--guard", type=int, nargs="+", default=None,
        help="Guardian levels to include (default: all 1-5). Example: --guard 2 4",
    )
    tournament_parser.add_argument("--adv-model", type=str, default=None, help="LLM model for adversarials (default: config)")
    tournament_parser.add_argument("--guard-model", type=str, default=None, help="LLM model for guardians (default: config)")
    tournament_parser.add_argument("--verbose", action="store_true", help="Show full conversations")

    # Seed command
    seed_parser = subparsers.add_parser("seed", help="Register all combatants in the DB (no battles)")
    seed_parser.add_argument("--model", type=str, default=None, help="LLM model to seed combatants for (default: config)")

    # Leaderboard command
    lb_parser = subparsers.add_parser("leaderboard", help="Show leaderboard")
    lb_parser.add_argument("--type", choices=["guardian", "adversarial"], help="Filter by type")

    # Reset command
    subparsers.add_parser("reset", help="Reset leaderboard")

    args = parser.parse_args()

    if args.command == "battle":
        adv_mc = {"model_id": args.adv_model} if args.adv_model else None
        guard_mc = {"model_id": args.guard_model} if args.guard_model else None
        asyncio.run(
            _run_with_db(
                run_battle(
                    adv_level=args.adv,
                    guard_level=args.guard,
                    max_turns=args.turns,
                    max_guesses=args.guesses,
                    adv_model_config=adv_mc,
                    guard_model_config=guard_mc,
                    verbose=not args.quiet,
                )
            )
        )
    elif args.command == "tournament":
        asyncio.run(
            _run_with_db(
                run_tournament(
                    max_turns=args.turns,
                    max_guesses=args.guesses,
                    rounds_per_matchup=args.rounds,
                    adv_levels=args.adv,
                    guard_levels=args.guard,
                    adv_model=args.adv_model,
                    guard_model=args.guard_model,
                    verbose=args.verbose,
                )
            )
        )
    elif args.command == "seed":
        asyncio.run(_run_with_db(seed_combatants(model_id=args.model)))
        asyncio.run(_run_with_db(seed_combatants()))
    elif args.command == "leaderboard":
        asyncio.run(_run_with_db(show_leaderboard(args.type)))
    elif args.command == "reset":
        asyncio.run(_run_with_db(reset_leaderboard()))
    else:
        parser.print_help()


async def _run_with_db(coro) -> None:
    """Initialize the DB tables before running the coroutine."""
    await init_db()
    await coro


if __name__ == "__main__":
    main()
