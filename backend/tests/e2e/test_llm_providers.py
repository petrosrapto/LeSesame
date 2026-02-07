"""
Le Sésame Backend - E2E LLM Provider Tests

Tests that the /chat endpoint works with different LLM providers and
OpenAI-compatible endpoint URLs by passing model_config in the request body.

Each test class targets a specific provider/endpoint. Tests are marked with
``@pytest.mark.requires_llm`` so they are automatically skipped when no LLM
is available, and additionally with a custom marker per provider so individual
providers can be selected or excluded with ``-m``.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import httpx
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_chat(
    http_client: httpx.Client,
    auth_headers: dict,
    message: str = "Hello, who are you?",
    level: int = 1,
    model_config: dict | None = None,
    timeout: float = 60.0,
) -> httpx.Response:
    """Send a chat message with an optional ``model_config`` override."""
    payload: dict = {"message": message, "level": level}
    if model_config is not None:
        payload["model_config"] = model_config
    return http_client.post(
        "/api/game/chat",
        headers=auth_headers,
        json=payload,
        timeout=timeout,
    )


def _assert_chat_ok(response: httpx.Response) -> dict:
    """Assert common chat-response structure and return the JSON body."""
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0, "Response should not be empty"
    assert data["level"] >= 1
    return data


# ---------------------------------------------------------------------------
# Tests — Default (config.yaml provider)
# ---------------------------------------------------------------------------

class TestDefaultProvider:
    """Chat using the default provider configured in config.yaml."""

    @pytest.mark.requires_llm
    def test_default_provider_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(http_client, auth_headers)
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — Mistral
# ---------------------------------------------------------------------------

class TestMistralProvider:
    """Chat using Mistral provider."""

    @pytest.mark.requires_llm
    @pytest.mark.mistral
    def test_mistral_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "mistral",
                "model_id": "mistral-small-latest",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — OpenAI (standard)
# ---------------------------------------------------------------------------

class TestOpenAIProvider:
    """Chat using the standard OpenAI endpoint."""

    @pytest.mark.requires_llm
    @pytest.mark.openai
    def test_openai_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "openai",
                "model_id": "gpt-4o-mini",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — DeepSeek (OpenAI-compatible)
# ---------------------------------------------------------------------------

class TestDeepSeekProvider:
    """Chat via the DeepSeek OpenAI-compatible endpoint."""

    @pytest.mark.requires_llm
    @pytest.mark.deepseek
    def test_deepseek_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "openai",
                "model_id": "deepseek-chat",
                "endpoint_url": "https://api.deepseek.com",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — Alibaba / DashScope (OpenAI-compatible)
# ---------------------------------------------------------------------------

class TestAlibabaProvider:
    """Chat via the Alibaba DashScope OpenAI-compatible endpoint."""

    @pytest.mark.requires_llm
    @pytest.mark.alibaba
    def test_alibaba_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "openai",
                "model_id": "qwen2.5-72b-instruct",
                "endpoint_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — Together AI (OpenAI-compatible)
# ---------------------------------------------------------------------------

class TestTogetherProvider:
    """Chat via the Together AI OpenAI-compatible endpoint."""

    @pytest.mark.requires_llm
    @pytest.mark.together
    def test_together_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "openai",
                "model_id": "openai/gpt-oss-120b",
                "endpoint_url": "https://api.together.xyz/v1",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — vLLM (OpenAI-compatible)
# ---------------------------------------------------------------------------

class TestVLLMProvider:
    """Chat via a self-hosted vLLM OpenAI-compatible endpoint."""

    @pytest.mark.requires_llm
    @pytest.mark.vllm
    @pytest.mark.skip(reason="vLLM endpoint is currently unavailable")
    def test_vllm_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "openai",
                "model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
                "endpoint_url": "http://52.206.209.94:8000/v1",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — Google Generative AI
# ---------------------------------------------------------------------------

class TestGoogleProvider:
    """Chat using Google Generative AI (Gemini)."""

    @pytest.mark.requires_llm
    @pytest.mark.google
    def test_google_gemini_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "google",
                "model_id": "gemini-2.0-flash",
            },
        )
        _assert_chat_ok(response)

    @pytest.mark.requires_llm
    @pytest.mark.google
    def test_google_gemma_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "google",
                "model_id": "gemma-3-27b-it",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — AWS Bedrock
# ---------------------------------------------------------------------------

class TestBedrockProvider:
    """Chat using AWS Bedrock."""

    @pytest.mark.requires_llm
    @pytest.mark.bedrock
    def test_bedrock_chat(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "provider": "bedrock",
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            },
        )
        _assert_chat_ok(response)


# ---------------------------------------------------------------------------
# Tests — Custom args override
# ---------------------------------------------------------------------------

class TestModelArgsOverride:
    """Verify that per-request args (temperature, max_tokens) are honoured."""

    @pytest.mark.requires_llm
    def test_custom_temperature_and_max_tokens(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
    ):
        """Chat with explicit temperature and max_tokens overrides."""
        http_client.post("/api/game/session", headers=auth_headers)
        response = _send_chat(
            http_client,
            auth_headers,
            model_config={
                "args": {"temperature": 0.1, "max_tokens": 256},
            },
        )
        data = _assert_chat_ok(response)
        # The response might be short because of the low max_tokens, but
        # we only assert it arrived successfully.
        assert data["response"]
