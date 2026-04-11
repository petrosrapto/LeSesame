"""
Le Sésame Backend - CAPTCHA Verification (Google reCAPTCHA v3)

Server-side verification of reCAPTCHA v3 tokens.

Author: Petros Raptopoulos
"""

import httpx

from ..core import settings, logger

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_recaptcha(token: str, expected_action: str | None = None) -> bool:
    """Verify a reCAPTCHA v3 token with Google.

    Returns True when the token is valid and the score meets the threshold.
    When RECAPTCHA_SECRET_KEY is not configured, verification is skipped
    (allows running locally without captcha).
    """
    if not settings.recaptcha_secret_key:
        logger.debug("reCAPTCHA secret not configured – skipping verification")
        return True

    if settings.recaptcha_bypass_token and token == settings.recaptcha_bypass_token:
        logger.debug("reCAPTCHA bypassed with test token")
        return True

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.recaptcha_secret_key,
                    "response": token,
                },
            )
            data = resp.json()

        if not data.get("success"):
            logger.warning(f"reCAPTCHA verification failed: {data.get('error-codes')}")
            return False

        score = data.get("score", 0.0)
        if score < settings.recaptcha_score_threshold:
            logger.warning(f"reCAPTCHA score too low: {score}")
            return False

        if expected_action and data.get("action") != expected_action:
            logger.warning(
                f"reCAPTCHA action mismatch: expected={expected_action}, got={data.get('action')}"
            )
            return False

        return True

    except Exception as exc:
        logger.error(f"reCAPTCHA verification error: {exc}")
        return False
