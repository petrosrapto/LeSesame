"""
Le Sésame Backend - E2E Audio Transcription Tests

Tests for the /api/game/transcribe endpoint against the running API.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import httpx
import pytest


class TestTranscribeEndpoint:
    """Test the audio transcription endpoint."""

    def test_transcribe_unauthenticated_fails(self, http_client: httpx.Client):
        """Test that transcription requires authentication."""
        response = http_client.post(
            "/api/game/transcribe",
            files={"file": ("test.webm", b"fake-audio-content", "audio/webm")},
        )
        assert response.status_code == 401

    def test_transcribe_unsupported_format(
        self, http_client: httpx.Client, auth_headers: dict
    ):
        """Test rejection of unsupported audio formats."""
        response = http_client.post(
            "/api/game/transcribe",
            headers=auth_headers,
            files={"file": ("test.txt", b"not audio", "text/plain")},
        )
        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()

    def test_transcribe_empty_file(
        self, http_client: httpx.Client, auth_headers: dict
    ):
        """Test rejection of empty audio files."""
        response = http_client.post(
            "/api/game/transcribe",
            headers=auth_headers,
            files={"file": ("test.webm", b"", "audio/webm")},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_transcribe_codec_params_accepted(
        self, http_client: httpx.Client, auth_headers: dict
    ):
        """Test that content types with codec params like 'audio/webm;codecs=opus' are accepted.

        We send a fake audio payload so the Mistral API will likely reject it,
        but the endpoint should NOT reject it at the content-type validation
        step. We accept either 200 (if Mistral somehow processes it) or 500
        (Mistral rejecting the invalid audio bytes).
        """
        response = http_client.post(
            "/api/game/transcribe",
            headers=auth_headers,
            files={"file": ("test.webm", b"fake-audio", "audio/webm;codecs=opus")},
        )
        # Should NOT be 400 for unsupported format — the codec param should be stripped
        assert response.status_code != 400 or "unsupported" not in response.json().get("detail", "").lower()
