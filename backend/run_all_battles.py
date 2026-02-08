"""
Run arena battles: all adversarial levels (1-5) vs guardian L1,
for every model in the frontend list (excluding bedrock).

Both guardian and adversarial use the SAME model per matchup so that
the combatant_id stored in the leaderboard aligns with the seeded entries.

Usage (inside the backend container):
    python /app/run_all_battles.py
"""

import asyncio
import traceback
from typing import Dict, Any, Optional, List

from app.services.arena.engine import ArenaEngine
from app.services.arena.models import BattleConfig, CombatantType
from app.services.arena.leaderboard import Leaderboard
from app.db.database import async_session_maker, init_db


# ── Model definitions (mirroring frontend, excluding bedrock) ─────────────
# Each entry: (display_name, model_id, provider, endpoint_url or None)

MODELS: List[tuple] = [
    # --- Mistral (native) ---
    ("Mistral Large 3",          "mistral-large-2512",               "mistral",   None),
    ("Mistral Medium 3.1",       "mistral-medium-2508",              "mistral",   None),
    ("Mistral Small 3.2",        "mistral-small-2506",               "mistral",   None),
    ("Ministral 3 14B",          "ministral-14b-2512",               "mistral",   None),
    ("Ministral 3 8B",           "ministral-8b-2512",                "mistral",   None),
    ("Ministral 3 3B",           "ministral-3b-2512",                "mistral",   None),
    ("Magistral Medium 1.2",     "magistral-medium-2509",            "mistral",   None),
    ("Magistral Small 1.2",      "magistral-small-2509",             "mistral",   None),
    ("Mistral Nemo 12B",         "open-mistral-nemo",                "mistral",   None),
    ("Codestral",                "codestral-2508",                   "mistral",   None),
    # --- Google (native) ---
    ("Gemini 3 Pro",             "gemini-3-pro-preview",             "google",    None),
    ("Gemini 3 Flash",           "gemini-3-flash-preview",           "google",    None),
    ("Gemini 2.5 Pro",           "gemini-2.5-pro",                   "google",    None),
    ("Gemini 2.5 Flash",         "gemini-2.5-flash",                 "google",    None),
    ("Gemini 2.0 Flash",         "gemini-2.0-flash",                 "google",    None),
    # --- Anthropic (native) ---
    ("Claude Opus 4.6",          "claude-opus-4-6",                  "anthropic", None),
    ("Claude Opus 4.5",          "claude-opus-4-5-20251101",         "anthropic", None),
    ("Claude Sonnet 4.5",        "claude-sonnet-4-5-20250929",       "anthropic", None),
    ("Claude Haiku 4.5",         "claude-haiku-4-5-20251001",        "anthropic", None),
    ("Claude Opus 4.1",          "claude-opus-4-1-20250805",         "anthropic", None),
    ("Claude Opus 4",            "claude-opus-4-20250514",           "anthropic", None),
    ("Claude Sonnet 4",          "claude-sonnet-4-20250514",         "anthropic", None),
    ("Claude Sonnet 3.7",        "claude-3-7-sonnet-20250219",       "anthropic", None),
    ("Claude Haiku 3.5",         "claude-3-5-haiku-20241022",        "anthropic", None),
    ("Claude Haiku 3",           "claude-3-haiku-20240307",          "anthropic", None),
    # --- OpenAI (native) ---
    ("GPT-5",                    "gpt-5",                            "openai",    None),
    ("GPT-5 mini",               "gpt-5-mini",                      "openai",    None),
    ("GPT-4.1",                  "gpt-4.1",                         "openai",    None),
    ("GPT-4.1 mini",             "gpt-4.1-mini",                    "openai",    None),
    ("GPT-4.1 nano",             "gpt-4.1-nano",                    "openai",    None),
    ("GPT-4o",                   "gpt-4o",                          "openai",    None),
    ("GPT-4o mini",              "gpt-4o-mini",                     "openai",    None),
    ("o4 mini",                  "o4-mini",                         "openai",    None),
    ("o3",                       "o3",                              "openai",    None),
    ("o3 mini",                  "o3-mini",                         "openai",    None),
    # --- Alibaba / DashScope (OpenAI-compatible) ---
    ("Qwen3 Max",                "qwen3-max",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen Plus",                "qwen-plus",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen Flash",               "qwen-flash",                      "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("QwQ Plus",                 "qwq-plus",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 235B A22B",          "qwen3-235b-a22b",                 "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 32B",                "qwen3-32b",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 30B A3B",            "qwen3-30b-a3b",                   "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 14B",                "qwen3-14b",                       "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 8B",                 "qwen3-8b",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    ("Qwen3 4B",                 "qwen3-4b",                        "openai",    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    # --- DeepSeek (OpenAI-compatible) ---
    ("DeepSeek V3",              "deepseek-chat",                   "openai",    "https://api.deepseek.com"),
    ("DeepSeek R1",              "deepseek-reasoner",               "openai",    "https://api.deepseek.com"),
    # --- TogetherAI (OpenAI-compatible) ---
    ("DeepSeek R1 0528",         "deepseek-ai/DeepSeek-R1-0528",                      "openai", "https://api.together.xyz/v1"),
    ("DeepSeek V3.1",            "deepseek-ai/DeepSeek-V3-0324",                      "openai", "https://api.together.xyz/v1"),
    ("Kimi K2",                  "moonshotai/Kimi-K2-Instruct",                       "openai", "https://api.together.xyz/v1"),
    ("Qwen3 235B (Together)",    "Qwen/Qwen3-235B-A22B",                              "openai", "https://api.together.xyz/v1"),
    ("Llama 4 Maverick",         "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "openai", "https://api.together.xyz/v1"),
    ("Llama 4 Scout",            "meta-llama/Llama-4-Scout-17B-16E-Instruct",         "openai", "https://api.together.xyz/v1"),
    ("Llama 3.3 70B Turbo",      "meta-llama/Llama-3.3-70B-Instruct-Turbo",           "openai", "https://api.together.xyz/v1"),
    ("Gemma 3 27B",              "google/gemma-3-27b-it",                             "openai", "https://api.together.xyz/v1"),
    ("GLM-4 7B",                 "THUDM/GLM-4.1V-9B-Thinking",                       "openai", "https://api.together.xyz/v1"),
    ("Cogito V2.1 671B",         "deepcogito/cogito-v2.1-preview-llama-70B",          "openai", "https://api.together.xyz/v1"),
]

ADV_LEVELS = [1, 2, 3, 4, 5]
GUARDIAN_LEVELS = [1, 2, 3, 4, 5]
MAX_TURNS = 10
MAX_GUESSES = 3
CONCURRENCY = 5  # Number of parallel battles


def build_model_config(model_id: str, provider: str, endpoint_url: Optional[str]) -> Dict[str, Any]:
    """Build a model_config dict for get_llm()."""
    cfg: Dict[str, Any] = {
        "provider": provider,
        "model_id": model_id,
    }
    if endpoint_url:
        cfg["endpoint_url"] = endpoint_url
    return cfg


async def run_single_battle(
    sem: asyncio.Semaphore,
    battle_num: int,
    total_battles: int,
    display_name: str,
    model_id: str,
    provider: str,
    endpoint_url: Optional[str],
    guard_level: int,
    adv_level: int,
    results: List[tuple],
    lock: asyncio.Lock,
) -> bool:
    """Run a single battle, respecting the concurrency semaphore. Returns True on success."""
    label = f"[{battle_num}/{total_battles}] Adv L{adv_level} vs Guard L{guard_level} [{display_name} / {model_id}]"
    async with sem:
        try:
            model_config = build_model_config(model_id, provider, endpoint_url)
            config = BattleConfig(
                guardian_level=guard_level,
                adversarial_level=adv_level,
                max_turns=MAX_TURNS,
                max_guesses=MAX_GUESSES,
                guardian_model_config=model_config,
                adversarial_model_config=model_config,
            )

            engine = ArenaEngine(config)
            result = await engine.run_battle()

            # Record in leaderboard
            async with async_session_maker() as session:
                leaderboard = Leaderboard(session)
                result = await leaderboard.record_battle(result)
                await session.commit()

            outcome = "ADV WINS" if result.adversarial_won else "GUARD WINS"
            async with lock:
                print(f"  {label} ... {outcome} (turns={result.total_turns}, guesses={len(result.guesses)})")
                results.append((label, outcome, None))
            return True

        except Exception as e:
            err_msg = str(e)[:120]
            async with lock:
                print(f"  {label} ... ERROR: {err_msg}")
                results.append((label, "ERROR", err_msg))
            return False


async def main():
    await init_db()

    total_models = len(MODELS)
    total_adv = len(ADV_LEVELS)
    total_guard = len(GUARDIAN_LEVELS)
    total_battles = total_models * total_adv * total_guard
    print(f"\n{'=' * 80}")
    print(f"  LE SESAME ARENA — PARALLEL BATTLE RUN (concurrency={CONCURRENCY})")
    print(f"  {total_models} models x {total_guard} guardian levels x {total_adv} adversarial levels = {total_battles} battles")
    print(f"  Guardian levels: {GUARDIAN_LEVELS} | Max turns: {MAX_TURNS} | Max guesses: {MAX_GUESSES}")
    print(f"{'=' * 80}\n")

    results_summary: List[tuple] = []
    sem = asyncio.Semaphore(CONCURRENCY)
    lock = asyncio.Lock()

    # Build work list: guardian level → adversarial level → model (sequential order)
    work = []
    for guard_level in GUARDIAN_LEVELS:
        for adv_level in ADV_LEVELS:
            for display_name, model_id, provider, endpoint_url in MODELS:
                work.append((display_name, model_id, provider, endpoint_url, guard_level, adv_level))

    # Launch all battles as concurrent tasks (semaphore limits parallelism)
    tasks = []
    for i, (display_name, model_id, provider, endpoint_url, guard_level, adv_level) in enumerate(work, 1):
        task = asyncio.create_task(
            run_single_battle(
                sem, i, total_battles,
                display_name, model_id, provider, endpoint_url,
                guard_level, adv_level,
                results_summary, lock,
            )
        )
        tasks.append(task)

    # Wait for all battles to complete
    outcomes = await asyncio.gather(*tasks)
    successes = sum(1 for ok in outcomes if ok)
    failures = sum(1 for ok in outcomes if not ok)

    # Final summary
    print(f"\n{'=' * 80}")
    print(f"  BATTLE RUN COMPLETE")
    print(f"  Successes: {successes} | Failures: {failures} | Total: {total_battles}")
    print(f"{'=' * 80}")

    # Show leaderboard
    async with async_session_maker() as session:
        leaderboard = Leaderboard(session)
        print(await leaderboard.display_rankings(CombatantType.GUARDIAN))
        print(await leaderboard.display_rankings(CombatantType.ADVERSARIAL))

    # Print failed battles
    if failures > 0:
        print(f"\n  FAILED BATTLES ({failures}):")
        for label, outcome, err in results_summary:
            if outcome == "ERROR":
                print(f"    {label}: {err}")


if __name__ == "__main__":
    asyncio.run(main())
