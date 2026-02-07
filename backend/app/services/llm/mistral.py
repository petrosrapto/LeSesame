"""
Le Sésame Backend - Mistral LLM Provider

LangChain wrapper for Mistral AI.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from langchain_mistralai import ChatMistralAI

from ...core import logger


def get_mistral_llm(model_id: str, api_key: str, **kwargs):
    """
    Returns an instance of Mistral's LLM with additional parameters.

    Args:
        model_id (str): The Mistral model ID to use.
        api_key (str): The Mistral API key.
        **kwargs: Additional arguments (e.g., max_tokens, temperature).

    Returns:
        ChatMistralAI: Configured instance of Mistral's model.
    """
    if not api_key:
        logger.warning("Mistral API key not provided")
        return None
    
    return ChatMistralAI(
        model=model_id,
        api_key=api_key,
        **kwargs
    )
