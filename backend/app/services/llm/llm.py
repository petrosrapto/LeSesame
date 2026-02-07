"""
Le Sésame Backend - LLM Factory

Factory function to get the configured LLM provider.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import Optional, Dict, Any

from .mistral import get_mistral_llm
from .openai import get_openai_llm
from .google import get_google_llm
from .bedrock import get_bedrock_llm
from .anthropic import get_anthropic_llm
from ...core import settings, logger


# Mapping of known OpenAI-compatible endpoint URLs to their API key setting names
ENDPOINT_API_KEY_MAP: Dict[str, str] = {
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1": "alibaba_api_key",
    "https://api.deepseek.com": "deepseek_api_key",
    "http://52.206.209.94:8000/v1": "vllm_api_key",
    "https://api.together.xyz/v1": "together_api_key",
}


def _resolve_openai_api_key(endpoint_url: Optional[str]) -> str:
    """
    Resolve the correct API key based on the endpoint URL.

    Different OpenAI-compatible providers (DeepSeek, Alibaba, Together, vLLM)
    require their own API keys. This maps the endpoint URL to the right key.

    Args:
        endpoint_url: The custom endpoint URL, or None for standard OpenAI.

    Returns:
        The resolved API key string.

    Raises:
        ValueError: If the endpoint requires a key that is not configured.
    """
    if not endpoint_url:
        return settings.openai_api_key

    key_attr = ENDPOINT_API_KEY_MAP.get(endpoint_url)
    if key_attr:
        api_key = getattr(settings, key_attr, "")
        if not api_key:
            raise ValueError(
                f"Endpoint '{endpoint_url}' requires {key_attr.upper()} to be set."
            )
        return api_key

    # Fall back to the default OpenAI key for unknown endpoints
    return settings.openai_api_key


def get_llm(model_config: Optional[Dict[str, Any]] = None):
    """
    Returns the LLM based on an optional per-request model configuration
    dictionary, falling back to the defaults defined in config.yaml.

    ``model_config`` mirrors the structure used by the MCP client::

        {
            "provider": "openai",          # or "mistral", "google", "bedrock"
            "model_id": "gpt-4o",
            "endpoint_url": "...",          # optional, OpenAI-compatible URL
            "args": {                       # optional extra kwargs
                "temperature": 0.5,
                "max_tokens": 2048
            }
        }

    When a key is absent the YAML / settings default is used.

    Args:
        model_config: Optional per-request model configuration dict.

    Returns:
        An instance of the configured LLM.

    Raises:
        ValueError: If the provider is unknown or creation fails.
    """
    model_config = model_config or {}

    provider = (model_config.get("provider") or settings.llm_provider).lower()
    model = model_config.get("model_id") or settings.llm_model
    endpoint_url = model_config.get("endpoint_url") or (settings.openai_endpoint_url or None)
    extra_args: Dict[str, Any] = model_config.get("args", {})

    # Build kwargs: YAML defaults ← request overrides
    kwargs: Dict[str, Any] = {
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
    }
    kwargs.update(extra_args)

    logger.info(f"Creating LLM — provider={provider}, model={model}, endpoint_url={endpoint_url}")

    llm = None

    if provider == "mistral":
        llm = get_mistral_llm(
            model_id=model,
            api_key=settings.mistral_api_key,
            **kwargs,
        )
    elif provider == "openai":
        api_key = _resolve_openai_api_key(endpoint_url)
        llm = get_openai_llm(
            model_id=model,
            api_key=api_key,
            endpoint_url=endpoint_url,
            **kwargs,
        )
    elif provider == "google":
        llm = get_google_llm(
            model_id=model,
            api_key=settings.google_api_key,
            **kwargs,
        )
    elif provider == "bedrock":
        llm = get_bedrock_llm(
            model_id=model,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
            **kwargs,
        )
    elif provider == "anthropic":
        llm = get_anthropic_llm(
            model_id=model,
            api_key=settings.anthropic_api_key,
            **kwargs,
        )
    else:
        raise ValueError(
            f"Unknown LLM provider '{provider}'. "
            f"Supported: mistral, openai, google, bedrock, anthropic"
        )

    if llm is None:
        raise ValueError(
            f"Failed to create LLM for provider '{provider}'. Check API credentials."
        )

    return llm
