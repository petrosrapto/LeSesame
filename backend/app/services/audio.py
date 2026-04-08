"""
Le Sésame Backend - Audio Transcription Service

Uses Mistral's Voxtral Mini Transcribe for speech-to-text conversion.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import os
from typing import Optional

from ..core import settings, logger

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None  # type: ignore[assignment, misc]


# Supported audio MIME types and their file extensions
SUPPORTED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/mp4",
    "audio/flac",
    "audio/x-wav",
    "audio/x-m4a",
    "audio/m4a",
}

# Max audio file size: 25 MB
MAX_AUDIO_SIZE = 25 * 1024 * 1024

# Model for transcription
TRANSCRIPTION_MODEL = "voxtral-mini-latest"


def _get_mistral_client() -> "Mistral":
    """Get an authenticated Mistral client."""
    if Mistral is None:
        raise ImportError("mistralai package is required for audio transcription. Install it with: pip install mistralai")
    api_key = settings.mistral_api_key or os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not configured")
    return Mistral(api_key=api_key)


async def transcribe_audio(
    audio_data: bytes,
    filename: str,
    language: Optional[str] = None,
) -> dict:
    """
    Transcribe audio data using Mistral's Voxtral Mini Transcribe.

    Args:
        audio_data: Raw audio bytes.
        filename: Original filename (used to determine format).
        language: Optional ISO 639-1 language code (e.g. "en", "fr").

    Returns:
        dict with "text" (full transcription) and optional "segments".
    """
    if len(audio_data) > MAX_AUDIO_SIZE:
        raise ValueError(f"Audio file too large. Maximum size is {MAX_AUDIO_SIZE // (1024*1024)} MB.")

    client = _get_mistral_client()

    logger.info(f"Transcribing audio file: {filename} ({len(audio_data)} bytes)")

    # Build transcription kwargs
    kwargs: dict = {
        "model": TRANSCRIPTION_MODEL,
        "file": {
            "content": audio_data,
            "file_name": filename,
        },
    }

    if language:
        kwargs["language"] = language

    try:
        response = client.audio.transcriptions.complete(**kwargs)

        text = response.text if hasattr(response, "text") else str(response)

        logger.info(f"Transcription completed: {len(text)} characters")

        return {
            "text": text,
            "duration": getattr(response, "duration", None),
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise
