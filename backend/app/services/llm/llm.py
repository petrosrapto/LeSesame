"""
Le Sésame Backend - LLM Factory

Factory function to get the configured LLM provider.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import Optional
from functools import lru_cache

from .mistral import get_mistral_llm
from .openai import get_openai_llm
from .google import get_google_llm
from .bedrock import get_bedrock_llm
from ...core import settings, logger


@lru_cache()
def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
):
    """
    Returns the LLM based on configuration.

    The provider can be:
        - "mistral": Mistral AI
        - "openai": OpenAI (also supports custom endpoints)
        - "google": Google Generative AI (Gemini, Gemma)
        - "bedrock": AWS Bedrock

    Args:
        provider: LLM provider name. Defaults to settings.llm_provider.
        model: Model ID to use. Defaults to settings.llm_model.
        **kwargs: Additional arguments passed to the LLM constructor.
        
    Returns:
        An instance of the configured LLM.
        
    Raises:
        ValueError: If provider is unknown or LLM creation fails.
    """
    provider = (provider or settings.llm_provider).lower()
    model = model or settings.llm_model
    
    # Default kwargs from settings
    default_kwargs = {
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
    }
    default_kwargs.update(kwargs)
    
    llm = None
    
    if provider == "mistral":
        llm = get_mistral_llm(
            model_id=model,
            api_key=settings.mistral_api_key,
            **default_kwargs
        )
    elif provider == "openai":
        llm = get_openai_llm(
            model_id=model,
            api_key=settings.openai_api_key,
            endpoint_url=getattr(settings, 'openai_endpoint_url', None),
            **default_kwargs
        )
    elif provider == "google":
        llm = get_google_llm(
            model_id=model,
            api_key=settings.google_api_key,
            **default_kwargs
        )
    elif provider == "bedrock":
        llm = get_bedrock_llm(
            model_id=model,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
            **default_kwargs
        )
    else:
        raise ValueError(f"Unknown LLM provider '{provider}'. Supported: mistral, openai, google, bedrock")
    
    if llm is None:
        raise ValueError(f"Failed to create LLM for provider '{provider}'. Check API credentials.")
    
    return llm
