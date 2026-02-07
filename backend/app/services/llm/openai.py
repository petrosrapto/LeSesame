"""
Le Sésame Backend - OpenAI LLM Provider

LangChain wrapper for OpenAI.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from langchain_openai import ChatOpenAI

from ...core import logger


def get_openai_llm(model_id: str, api_key: str, endpoint_url: str = None, **kwargs):
    """
    Returns an instance of OpenAI's LLM with additional parameters.

    Args:
        model_id (str): The OpenAI model name or ID to use.
        api_key (str): The OpenAI API key.
        endpoint_url (str, optional): Custom endpoint URL for API requests.
        **kwargs: Additional arguments (e.g., max_tokens, temperature).

    Returns:
        ChatOpenAI: Configured instance of OpenAI's model.
    """
    if not api_key:
        logger.warning("OpenAI API key not provided")
        return None
    
    if endpoint_url:
        kwargs["base_url"] = endpoint_url
    
    return ChatOpenAI(
        model=model_id,
        api_key=api_key,
        **kwargs
    )
