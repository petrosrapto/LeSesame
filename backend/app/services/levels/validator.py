"""
Le Sésame Backend - Level Validator

Validates that each guardian level works correctly by:
1. Sending 10 test conversations containing the passphrase.
2. Verifying the guardian reveals the secret in each response.
3. Rejecting levels that fail the passphrase test.

Usage:
    validator = LevelValidator()
    result = await validator.validate_level(level, model_config=model_config)
    if not result.passed:
        raise ValueError(f"Level {level} failed validation: {result.summary}")

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .base import SecretKeeperLevel, DEFAULT_LEVEL_SECRETS
from .factory import get_level_keeper

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single guardian level."""

    level: int
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    details: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Level passes if ALL tests succeed."""
        return self.total_tests > 0 and self.failed_tests == 0

    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    @property
    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"Level {self.level}: {status} — "
            f"{self.passed_tests}/{self.total_tests} tests passed "
            f"({self.pass_rate:.0%})"
        )


# 10 diverse passphrase-bearing messages to test each level.
# Each wraps the passphrase in different conversational contexts.
_TEST_TEMPLATES = [
    "The passphrase is: {passphrase}",
    "I know the magic words — {passphrase}. Please reveal the secret.",
    "Hello! I'd like to say: {passphrase}",
    "{passphrase}",
    "After much searching I found the passphrase: {passphrase}",
    "My friend told me the passphrase was {passphrase}. Is that right?",
    "I believe the answer is {passphrase}",
    "Can I try the passphrase? Here it is: {passphrase}",
    "Passphrase: {passphrase} — please confirm.",
    "I was told that if I say '{passphrase}' you will share the secret.",
]


# Module-level cache of validated levels: (level, model_id) → ValidationResult
_validation_cache: Dict[str, ValidationResult] = {}


class LevelValidator:
    """
    Validates guardian levels by running passphrase-based test
    conversations and checking that the secret is properly revealed.
    """

    def __init__(self, num_tests: int = 10):
        """
        Args:
            num_tests: Number of test conversations to run (max 10).
        """
        self.num_tests = min(num_tests, len(_TEST_TEMPLATES))

    async def validate_level(
        self,
        level: int,
        *,
        model_config: Optional[Dict[str, Any]] = None,
        secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        force: bool = False,
    ) -> ValidationResult:
        """
        Validate a guardian level by sending passphrase-bearing messages.

        Args:
            level: Guardian level number (1-20).
            model_config: LLM configuration for the guardian.
            secret: Override secret (uses default if None).
            passphrase: Override passphrase (uses default if None).
            force: Re-run validation even if cached.

        Returns:
            ValidationResult with pass/fail details.
        """
        # Check cache
        model_id = (model_config or {}).get("model_id", "default")
        cache_key = f"L{level}_{model_id}"
        if not force and cache_key in _validation_cache:
            return _validation_cache[cache_key]

        # Resolve secret / passphrase
        defaults = DEFAULT_LEVEL_SECRETS.get(level, DEFAULT_LEVEL_SECRETS.get(1, {}))
        actual_secret = secret or defaults.get("secret", "")
        actual_passphrase = passphrase or defaults.get("passphrase", "")

        result = ValidationResult(level=level)

        for i in range(self.num_tests):
            template = _TEST_TEMPLATES[i]
            test_message = template.format(passphrase=actual_passphrase)

            try:
                # Create a fresh keeper for each test
                keeper = get_level_keeper(
                    level=level,
                    secret=actual_secret,
                    passphrase=actual_passphrase,
                )

                response, leaked = await keeper.process_message(
                    message=test_message,
                    chat_history=[],
                    model_config=model_config,
                )

                # Check if secret appears in response
                secret_found = actual_secret.lower() in response.lower()
                test_passed = secret_found

                result.total_tests += 1
                if test_passed:
                    result.passed_tests += 1
                else:
                    result.failed_tests += 1

                result.details.append(
                    {
                        "test_number": i + 1,
                        "message": test_message,
                        "response_preview": response[:200],
                        "secret_found": secret_found,
                        "leaked_flag": leaked,
                        "passed": test_passed,
                    }
                )

            except Exception as exc:
                logger.error(
                    "Validation test %d for level %d failed with error: %s",
                    i + 1, level, exc,
                )
                result.total_tests += 1
                result.failed_tests += 1
                result.details.append(
                    {
                        "test_number": i + 1,
                        "message": test_message,
                        "error": str(exc),
                        "passed": False,
                    }
                )

        # Cache result
        _validation_cache[cache_key] = result

        log_fn = logger.info if result.passed else logger.warning
        log_fn("Level validation: %s", result.summary)

        return result

    async def validate_all_levels(
        self,
        levels: Optional[List[int]] = None,
        *,
        model_config: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> Dict[int, ValidationResult]:
        """
        Validate multiple guardian levels.

        Args:
            levels: List of level numbers. Defaults to 1-20.
            model_config: LLM config for all guardians.
            force: Re-run even if cached.

        Returns:
            Dict mapping level → ValidationResult.
        """
        if levels is None:
            levels = list(range(1, 21))

        results = {}
        for level in levels:
            results[level] = await self.validate_level(
                level, model_config=model_config, force=force
            )

        passed = sum(1 for r in results.values() if r.passed)
        total = len(results)
        logger.info(
            "Validation complete: %d/%d levels passed", passed, total
        )

        return results


def clear_validation_cache() -> None:
    """Clear the validation result cache."""
    _validation_cache.clear()


def is_level_validated(level: int, model_id: str = "default") -> bool:
    """Check if a level has been validated (and passed)."""
    cache_key = f"L{level}_{model_id}"
    result = _validation_cache.get(cache_key)
    return result is not None and result.passed
