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
from .structured_output import get_structured_output, get_structured_output_metrics

__all__ = ["get_llm", "get_structured_output", "get_structured_output_metrics"]
