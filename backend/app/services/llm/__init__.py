"""
Le Sésame Backend - LLM Module

LangChain-based LLM providers with configurable backends.

Supported providers:
    - mistral: Mistral AI
    - openai: OpenAI (and compatible endpoints)
    - google: Google Generative AI (Gemini, Gemma)
    - bedrock: AWS Bedrock
    - anthropic: Anthropic (Claude)
"""

from .llm import get_llm

__all__ = ["get_llm"]
