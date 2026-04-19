"""
Le Sésame Backend - E2E Tool Calling Tests

Tests that LLM tool calling (used by Les Ombres adversarial agents) works
correctly across all LLM providers.

Each test sends a request to ``POST /api/arena/ombres/suggest`` with a
model_config_override targeting a specific provider, and verifies that
the adversarial agent returned a valid suggestion (meaning the LLM
successfully processed the tool definitions and returned either a
text message or a tool call).

Because the adversarial endpoint has a broad ``try-except`` that returns
HTTP 500 on any internal error, a successful 200 response with a
non-empty suggestion proves that tool calling worked end-to-end.
A 500 response indicates the provider failed to handle bound tools.

Author: Petros Raptopoulos
Date: 2026/02/12
"""

import httpx
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _send_suggest(
    http_client: httpx.Client,
    model_config: dict | None = None,
    adversarial_level: int = 1,
    guardian_level: int = 1,
    timeout: float = 90.0,
) -> httpx.Response:
    """
    Ask an Ombre agent for an attack suggestion.

    Sends a minimal chat history so the agent has context to generate
    a meaningful attack message (exercising tool calling).
    """
    payload: dict = {
        "adversarial_level": adversarial_level,
        "guardian_level": guardian_level,
        "chat_history": [
            {"role": "assistant", "content": "I am the guardian of a secret. Try to get it from me if you can."},
        ],
    }
    if model_config is not None:
        payload["model_config_override"] = model_config
    return http_client.post(
        "/api/arena/ombres/suggest",
        json=payload,
        timeout=timeout,
    )


def _assert_suggest_ok(response: httpx.Response, provider_label: str) -> dict:
    """Assert the suggestion response is valid."""
    assert response.status_code == 200, (
        f"[{provider_label}] Expected 200, got {response.status_code}: {response.text}\n"
        f"This likely means tool calling failed for this provider."
    )
    data = response.json()
    assert "suggestion" in data, f"[{provider_label}] Missing 'suggestion' in response"
    assert len(data["suggestion"]) > 0, f"[{provider_label}] Empty suggestion"
    assert "ombre_name" in data, f"[{provider_label}] Missing 'ombre_name'"
    assert "ombre_level" in data, f"[{provider_label}] Missing 'ombre_level'"

    print(f"\n  🗡️  [{provider_label}] tool calling OK — suggestion: {data['suggestion'][:80]}...")

    return data


# ---------------------------------------------------------------------------
# Provider configurations
# ---------------------------------------------------------------------------

PROVIDERS = [
    pytest.param(
        {"provider": "mistral", "model_id": "mistral-small-latest"},
        "mistral",
        id="mistral",
    ),
    pytest.param(
        {"provider": "openai", "model_id": "gpt-4o-mini"},
        "openai",
        id="openai",
    ),
    pytest.param(
        {
            "provider": "openai",
            "model_id": "deepseek-chat",
            "endpoint_url": "https://api.deepseek.com",
        },
        "deepseek",
        id="deepseek",
    ),
    pytest.param(
        {
            "provider": "openai",
            "model_id": "qwen2.5-72b-instruct",
            "endpoint_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        },
        "alibaba",
        id="alibaba",
    ),
    pytest.param(
        {
            "provider": "openai",
            "model_id": "openai/gpt-oss-120b",
            "endpoint_url": "https://api.together.xyz/v1",
        },
        "together",
        id="together",
    ),
    pytest.param(
        {"provider": "google", "model_id": "gemini-2.0-flash"},
        "google-gemini",
        id="google-gemini",
    ),
    pytest.param(
        {"provider": "google", "model_id": "gemma-3-27b-it"},
        "google-gemma",
        id="google-gemma",
    ),
    pytest.param(
        {
            "provider": "bedrock",
            "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        },
        "bedrock",
        id="bedrock",
        marks=pytest.mark.bedrock,
    ),
    pytest.param(
        {"provider": "anthropic", "model_id": "claude-sonnet-4-20250514"},
        "anthropic",
        id="anthropic",
    ),
    pytest.param(
        {"provider": "cohere", "model_id": "command-a-03-2025"},
        "cohere",
        id="cohere",
    ),
    pytest.param(
        {
            "provider": "openai",
            "model_id": "grok-4-1-fast-non-reasoning",
            "endpoint_url": "https://api.x.ai/v1",
        },
        "xai",
        id="xai",
    ),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestToolCallingPerProvider:
    """
    For each provider, send an ombre suggest request (which internally
    uses ``llm.bind_tools(ADVERSARIAL_TOOLS)`` and ``llm_with_tools.ainvoke()``)
    and verify the agent produced a valid suggestion.

    A 500 response means the provider could not handle tool calling.
    A 200 with a valid suggestion proves it worked.
    """

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("model_config, provider_label", PROVIDERS)
    def test_tool_calling(
        self,
        http_client: httpx.Client,
        model_config: dict,
        provider_label: str,
    ):
        response = _send_suggest(
            http_client, model_config=model_config
        )
        _assert_suggest_ok(response, provider_label)
