"""
Le Sésame Backend - Cohere LLM Provider

LangChain wrapper for Cohere (Command models).

Author: Petros Raptopoulos
Date: 2026/02/11
"""

from langchain_cohere import ChatCohere

from ...core import logger


def get_cohere_llm(model_id: str, api_key: str, **kwargs):
    """
    Returns an instance of Cohere's LLM with additional parameters.

    Args:
        model_id (str): The Cohere model ID to use (e.g. "command-a-03-2025").
        api_key (str): The Cohere API key.
        **kwargs: Additional arguments (e.g., max_tokens, temperature).

    Returns:
        ChatCohere: Configured instance of Cohere's model.
    """
    if not api_key:
        logger.warning("Cohere API key not provided")
        return None

    return ChatCohere(
        model=model_id,
        cohere_api_key=api_key,
        **kwargs,
    )
