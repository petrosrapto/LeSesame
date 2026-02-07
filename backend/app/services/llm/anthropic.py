"""
Le Sésame Backend - Anthropic LLM Provider

LangChain wrapper for Anthropic (Claude).

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from langchain_anthropic import ChatAnthropic

from ...core import logger


def get_anthropic_llm(model_id: str, api_key: str, **kwargs):
    """
    Returns an instance of Anthropic's Claude LLM with additional parameters.

    Args:
        model_id (str): The Anthropic model ID to use (e.g. "claude-sonnet-4-20250514").
        api_key (str): The Anthropic API key.
        **kwargs: Additional arguments (e.g., max_tokens, temperature).

    Returns:
        ChatAnthropic: Configured instance of Anthropic's model.
    """
    if not api_key:
        logger.warning("Anthropic API key not provided")
        return None

    return ChatAnthropic(
        model=model_id,
        api_key=api_key,
        **kwargs,
    )
