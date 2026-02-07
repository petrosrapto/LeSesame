"""
Le Sésame Backend - Audio Transcription Tests

Unit tests for the audio transcription service and endpoint.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.audio import (
    transcribe_audio,
    _get_mistral_client,
    SUPPORTED_AUDIO_TYPES,
    MAX_AUDIO_SIZE,
    TRANSCRIPTION_MODEL,
)


# ==================== Service-level tests ====================


class TestGetMistralClient:
    """Tests for Mistral client instantiation."""

    @patch("app.services.audio.settings")
    def test_client_with_api_key(self, mock_settings):
        """Test client creation when API key is configured."""
        mock_settings.mistral_api_key = "test-api-key"
        client = _get_mistral_client()
        assert client is not None

    @patch.dict("os.environ", {"MISTRAL_API_KEY": ""}, clear=False)
    @patch("app.services.audio.settings")
    def test_client_missing_api_key_raises(self, mock_settings):
        """Test that missing API key raises ValueError."""
        mock_settings.mistral_api_key = ""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
            _get_mistral_client()

    @patch.dict("os.environ", {"MISTRAL_API_KEY": "env-key"}, clear=False)
    @patch("app.services.audio.settings")
    def test_client_falls_back_to_env(self, mock_settings):
        """Test client falls back to environment variable."""
        mock_settings.mistral_api_key = ""
        client = _get_mistral_client()
        assert client is not None


class TestTranscribeAudio:
    """Tests for the transcribe_audio service function."""

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        mock_response = MagicMock()
        mock_response.text = "Hello, this is a test transcription."
        mock_response.duration = 5.2

        with patch("app.services.audio._get_mistral_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.audio.transcriptions.complete.return_value = mock_response
            mock_client_fn.return_value = mock_client

            result = await transcribe_audio(
                audio_data=b"fake-audio-data",
                filename="test.webm",
            )

        assert result["text"] == "Hello, this is a test transcription."
        assert result["duration"] == 5.2

        # Verify the API was called with correct params
        mock_client.audio.transcriptions.complete.assert_called_once()
        call_kwargs = mock_client.audio.transcriptions.complete.call_args[1]
        assert call_kwargs["model"] == TRANSCRIPTION_MODEL
        assert call_kwargs["file"]["file_name"] == "test.webm"
        assert "language" not in call_kwargs

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_language(self):
        """Test transcription with explicit language."""
        mock_response = MagicMock()
        mock_response.text = "Bonjour!"
        mock_response.duration = 1.0

        with patch("app.services.audio._get_mistral_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.audio.transcriptions.complete.return_value = mock_response
            mock_client_fn.return_value = mock_client

            result = await transcribe_audio(
                audio_data=b"fake-audio-data",
                filename="test.mp3",
                language="fr",
            )

        assert result["text"] == "Bonjour!"
        call_kwargs = mock_client.audio.transcriptions.complete.call_args[1]
        assert call_kwargs["language"] == "fr"

    @pytest.mark.asyncio
    async def test_transcribe_audio_no_text_attr(self):
        """Test transcription when response has no text attribute (fallback to str)."""
        mock_response = MagicMock(spec=[])  # No attributes

        with patch("app.services.audio._get_mistral_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.audio.transcriptions.complete.return_value = mock_response
            mock_client_fn.return_value = mock_client

            result = await transcribe_audio(
                audio_data=b"fake-audio-data",
                filename="test.wav",
            )

        # Falls back to str(response) when .text is absent
        assert isinstance(result["text"], str)

    @pytest.mark.asyncio
    async def test_transcribe_audio_too_large(self):
        """Test that oversized audio raises ValueError."""
        large_data = b"x" * (MAX_AUDIO_SIZE + 1)
        with pytest.raises(ValueError, match="too large"):
            await transcribe_audio(
                audio_data=large_data,
                filename="big.wav",
            )

    @pytest.mark.asyncio
    async def test_transcribe_audio_api_error(self):
        """Test that API errors propagate."""
        with patch("app.services.audio._get_mistral_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client.audio.transcriptions.complete.side_effect = RuntimeError("API error")
            mock_client_fn.return_value = mock_client

            with pytest.raises(RuntimeError, match="API error"):
                await transcribe_audio(
                    audio_data=b"fake-audio-data",
                    filename="test.webm",
                )


# ==================== Endpoint-level tests ====================


@pytest.fixture
async def auth_headers(client, sample_user_data):
    """Get authentication headers for a registered user."""
    response = await client.post("/api/auth/register", json=sample_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestTranscribeEndpoint:
    """Tests for the POST /api/game/transcribe endpoint."""

    @pytest.mark.asyncio
    async def test_transcribe_success(self, client, auth_headers):
        """Test successful transcription via endpoint."""
        with patch("app.routers.game.transcribe_audio") as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Hello world",
                "duration": 2.5,
            }

            response = await client.post(
                "/api/game/transcribe",
                headers=auth_headers,
                files={"file": ("test.webm", b"fake-audio", "audio/webm")},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello world"
        assert data["duration"] == 2.5

    @pytest.mark.asyncio
    async def test_transcribe_with_codec_params(self, client, auth_headers):
        """Test that content type with codec params (e.g. audio/webm;codecs=opus) is accepted."""
        with patch("app.routers.game.transcribe_audio") as mock_transcribe:
            mock_transcribe.return_value = {"text": "test", "duration": 1.0}

            response = await client.post(
                "/api/game/transcribe",
                headers=auth_headers,
                files={"file": ("test.webm", b"fake-audio", "audio/webm;codecs=opus")},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_transcribe_with_language(self, client, auth_headers):
        """Test transcription with language parameter."""
        with patch("app.routers.game.transcribe_audio") as mock_transcribe:
            mock_transcribe.return_value = {"text": "Bonjour", "duration": 1.0}

            response = await client.post(
                "/api/game/transcribe",
                headers=auth_headers,
                files={"file": ("test.webm", b"fake-audio", "audio/webm")},
                data={"language": "fr"},
            )

        assert response.status_code == 200
        # Verify language was passed
        mock_transcribe.assert_called_once()
        call_kwargs = mock_transcribe.call_args[1]
        assert call_kwargs["language"] == "fr"

    @pytest.mark.asyncio
    async def test_transcribe_unsupported_format(self, client, auth_headers):
        """Test rejection of unsupported audio format."""
        response = await client.post(
            "/api/game/transcribe",
            headers=auth_headers,
            files={"file": ("test.txt", b"not audio", "text/plain")},
        )

        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_transcribe_empty_file(self, client, auth_headers):
        """Test rejection of empty audio file."""
        response = await client.post(
            "/api/game/transcribe",
            headers=auth_headers,
            files={"file": ("test.webm", b"", "audio/webm")},
        )

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_transcribe_unauthenticated(self, client):
        """Test that transcription requires authentication."""
        response = await client.post(
            "/api/game/transcribe",
            files={"file": ("test.webm", b"fake-audio", "audio/webm")},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_transcribe_value_error(self, client, auth_headers):
        """Test that ValueError from transcription returns 400."""
        with patch("app.routers.game.transcribe_audio") as mock_transcribe:
            mock_transcribe.side_effect = ValueError("API key not configured")

            response = await client.post(
                "/api/game/transcribe",
                headers=auth_headers,
                files={"file": ("test.webm", b"fake-audio", "audio/webm")},
            )

        assert response.status_code == 400
        assert "api key" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_transcribe_internal_error(self, client, auth_headers):
        """Test that unexpected errors return 500."""
        with patch("app.routers.game.transcribe_audio") as mock_transcribe:
            mock_transcribe.side_effect = RuntimeError("Connection failed")

            response = await client.post(
                "/api/game/transcribe",
                headers=auth_headers,
                files={"file": ("test.webm", b"fake-audio", "audio/webm")},
            )

        assert response.status_code == 500
        assert "failed to transcribe" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_transcribe_various_audio_types(self, client, auth_headers):
        """Test that all supported audio MIME types are accepted."""
        for mime_type in ["audio/webm", "audio/wav", "audio/mp3", "audio/ogg", "audio/flac"]:
            with patch("app.routers.game.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = {"text": "ok", "duration": 1.0}

                response = await client.post(
                    "/api/game/transcribe",
                    headers=auth_headers,
                    files={"file": ("test", b"fake-audio", mime_type)},
                )

                assert response.status_code == 200, f"Failed for {mime_type}"
