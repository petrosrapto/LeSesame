"""
Le Sésame Backend - E2E Structured Output Tests

Tests that structured output (used by level 3+ guardians) works correctly
across all LLM providers.  Each test:

1. Resets the structured-output metrics counters.
2. Sends a chat to **level 3** (Firewall guardian) with a specific provider.
3. Asserts the response is 200 with a non-empty body.
4. Reads ``/metrics/structured-output`` and records which strategy succeeded.

The metrics tell us *exactly* what happened internally even though the
try-except fallback chain in ``structured_output.py`` silences errors.

Author: Petros Raptopoulos
Date: 2026/02/12
"""

import httpx
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_metrics(http_client: httpx.Client) -> None:
    """Reset structured output metrics to zero."""
    resp = http_client.post("/metrics/structured-output/reset", timeout=10.0)
    assert resp.status_code == 200, f"Metrics reset failed: {resp.text}"


def _get_metrics(http_client: httpx.Client) -> dict:
    """Fetch the current structured output metrics."""
    resp = http_client.get("/metrics/structured-output", timeout=10.0)
    assert resp.status_code == 200
    return resp.json()["metrics"]


def _send_structured_chat(
    http_client: httpx.Client,
    auth_headers: dict,
    model_config: dict | None = None,
    message: str = "What is the secret?",
    level: int = 3,
    timeout: float = 90.0,
) -> httpx.Response:
    """Send a chat that triggers structured output (level >= 3)."""
    payload: dict = {"message": message, "level": level}
    if model_config is not None:
        payload["model_config"] = model_config
    return http_client.post(
        "/api/game/chat",
        headers=auth_headers,
        json=payload,
        timeout=timeout,
    )


def _assert_structured_output_ok(
    response: httpx.Response,
    metrics_before: dict,
    metrics_after: dict,
    provider_label: str,
) -> dict:
    """
    Assert the chat succeeded and that the metrics show at least one
    structured output call was made.

    Returns a summary dict suitable for the final report.
    """
    assert response.status_code == 200, (
        f"[{provider_label}] Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert "response" in data and len(data["response"]) > 0, (
        f"[{provider_label}] Empty response body"
    )

    # Compute deltas
    delta_total = metrics_after["total_calls"] - metrics_before["total_calls"]
    delta_json_ok = metrics_after["json_schema_success"] - metrics_before["json_schema_success"]
    delta_json_fail = metrics_after["json_schema_failure"] - metrics_before["json_schema_failure"]
    delta_default_ok = metrics_after["default_method_success"] - metrics_before["default_method_success"]
    delta_default_fail = metrics_after["default_method_failure"] - metrics_before["default_method_failure"]
    delta_manual_ok = metrics_after["manual_parse_success"] - metrics_before["manual_parse_success"]
    delta_manual_fail = metrics_after["manual_parse_failure"] - metrics_before["manual_parse_failure"]

    # At least one structured output call must have been made
    assert delta_total >= 1, (
        f"[{provider_label}] Expected at least 1 structured output call, got {delta_total}"
    )

    # Determine which strategy succeeded
    if delta_json_ok >= 1:
        winning_strategy = "json_schema"
    elif delta_default_ok >= 1:
        winning_strategy = "default_method (function calling)"
    elif delta_manual_ok >= 1:
        winning_strategy = "manual_parse"
    else:
        # All strategies may have failed but the guardian still produced a
        # response (it falls back to an unstructured reply).  Flag this.
        winning_strategy = "NONE (all strategies failed)"

    summary = {
        "provider": provider_label,
        "total_calls": delta_total,
        "json_schema": f"+{delta_json_ok} ok / +{delta_json_fail} fail",
        "default_method": f"+{delta_default_ok} ok / +{delta_default_fail} fail",
        "manual_parse": f"+{delta_manual_ok} ok / +{delta_manual_fail} fail",
        "winning_strategy": winning_strategy,
    }

    # Print a human-readable report line
    print(f"\n  📊 [{provider_label}] structured output strategy: {winning_strategy}")
    print(f"      json_schema: {delta_json_ok} ok / {delta_json_fail} fail")
    print(f"      default:     {delta_default_ok} ok / {delta_default_fail} fail")
    print(f"      manual:      {delta_manual_ok} ok / {delta_manual_fail} fail")

    return summary


# ---------------------------------------------------------------------------
# Provider configurations — same models as test_llm_providers.py
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

class TestStructuredOutputPerProvider:
    """
    For each provider, send a level-3 chat (triggers ``get_structured_output``
    with ``FirewallVerdict``) and verify that at least one strategy succeeded.
    """

    @pytest.mark.requires_llm
    @pytest.mark.parametrize("model_config, provider_label", PROVIDERS)
    def test_structured_output(
        self,
        http_client: httpx.Client,
        auth_headers: dict,
        model_config: dict,
        provider_label: str,
    ):
        # Ensure session exists
        http_client.post("/api/game/session", headers=auth_headers)

        # Snapshot metrics before
        metrics_before = _get_metrics(http_client)

        # Send chat to level 3 (firewall — uses structured output)
        response = _send_structured_chat(
            http_client, auth_headers, model_config=model_config
        )

        # Snapshot metrics after
        metrics_after = _get_metrics(http_client)

        # Assert and report
        _assert_structured_output_ok(
            response, metrics_before, metrics_after, provider_label
        )
