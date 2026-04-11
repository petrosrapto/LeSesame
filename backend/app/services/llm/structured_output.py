"""
Le Sésame Backend - Structured Output Utility

Robust structured output helper with multiple fallback strategies.
Works across OpenAI, Anthropic, Mistral, and other LangChain providers.

Author: Petros Raptopoulos
Date: 2026/02/10
"""

import json
import re
from typing import TypeVar, Type, Optional, List
from pydantic import BaseModel, ValidationError
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from .google import GemmaGoogleChatModel
from ...core import logger

# Lazy imports to avoid circular dependencies; resolved at first call.
_ChatAnthropic = None
_ChatOpenAI = None


def _get_chat_anthropic():
    """Return the ChatAnthropic class (lazy import)."""
    global _ChatAnthropic
    if _ChatAnthropic is None:
        try:
            from langchain_anthropic import ChatAnthropic
            _ChatAnthropic = ChatAnthropic
        except ImportError:
            _ChatAnthropic = type(None)  # sentinel — never matches
    return _ChatAnthropic


def _get_chat_openai():
    """Return the ChatOpenAI class (lazy import)."""
    global _ChatOpenAI
    if _ChatOpenAI is None:
        try:
            from langchain_openai import ChatOpenAI
            _ChatOpenAI = ChatOpenAI
        except ImportError:
            _ChatOpenAI = type(None)
    return _ChatOpenAI


def _ensure_human_message(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Ensure the message list contains at least one HumanMessage.

    Some providers (notably Anthropic) separate SystemMessages into a
    dedicated ``system`` parameter, which can leave the ``messages`` array
    empty and trigger a 400 error.  When every message is a SystemMessage
    we convert the last one to a HumanMessage so the request is valid
    across all providers.
    """
    if all(isinstance(m, SystemMessage) for m in messages):
        converted = list(messages[:-1])
        converted.append(HumanMessage(content=messages[-1].content))
        return converted
    return messages


def _is_manual_parse_only(llm: BaseChatModel) -> bool:
    """Return True for models that only support manual-parse structured output.

    Gemma models do not support JSON mode or native function calling through
    the Google Generative AI API.  Attempting ``with_structured_output`` on
    them wastes two API round-trips before falling to Strategy 3 anyway, so
    we short-circuit here.
    """
    return isinstance(llm, GemmaGoogleChatModel)


def _is_openai_compatible(llm: BaseChatModel) -> bool:
    """Return True for ChatOpenAI instances pointing at non-OpenAI endpoints.

    OpenAI-compatible providers (DeepSeek, Alibaba/DashScope, Together, xAI,
    etc.) are accessed via ChatOpenAI with a custom ``base_url``.  These
    providers generally do NOT support ``response_format: {type: "json_schema"}``
    and ChatOpenAI's default ``with_structured_output`` method is ``json_schema``
    since langchain-openai >= 0.2.  We detect them here so we can route to
    ``method="function_calling"`` instead.
    """
    ChatOpenAI = _get_chat_openai()
    if not isinstance(llm, ChatOpenAI):
        return False
    base_url = str(getattr(llm, "openai_api_base", "") or "")
    # Native OpenAI uses the default base URL (api.openai.com) or no override
    if not base_url or "api.openai.com" in base_url:
        return False
    return True


def _skip_json_schema(llm: BaseChatModel) -> bool:
    """Return True for providers where ``method="json_schema"`` is known to fail.

    - Anthropic: ``with_structured_output(method="json_schema")`` triggers 400
      errors (empty messages, schema translation issues).
    - OpenAI-compatible providers (DeepSeek, Alibaba, Together, etc.): the
      ``json_schema`` response format type is unsupported by these APIs.
    """
    if isinstance(llm, _get_chat_anthropic()):
        return True
    if _is_openai_compatible(llm):
        return True
    return False


# Metrics for monitoring structured output success rates
_METRICS = {
    "json_schema_success": 0,
    "json_schema_failure": 0,
    "default_method_success": 0,
    "default_method_failure": 0,
    "manual_parse_success": 0,
    "manual_parse_failure": 0,
    "total_calls": 0,
}

T = TypeVar('T', bound=BaseModel)


async def get_structured_output(
    llm: BaseChatModel,
    schema: Type[T],
    messages: List[BaseMessage],
    fallback_to_manual_parse: bool = True,
) -> Optional[T]:
    """
    Attempts to get structured output from an LLM with multiple fallback strategies.

    Strategy:
    1. Try native structured output (method="json_schema") - most reliable
    2. Fall back to function calling (default method)
    3. Fall back to manual JSON extraction from raw LLM response

    Args:
        llm: The LangChain LLM instance
        schema: The Pydantic model class to parse into
        messages: The messages to send to the LLM
        fallback_to_manual_parse: If True, tries manual JSON parsing as final fallback

    Returns:
        An instance of the schema model, or None if all methods fail
    """
    _METRICS["total_calls"] += 1
    messages = _ensure_human_message(messages)

    # Fast path: models that only support manual parsing (e.g. Gemma)
    # Skip Strategies 1 & 2 to avoid wasted API calls and error noise.
    if _is_manual_parse_only(llm):
        logger.debug(
            f"Model only supports manual parse — skipping json_schema/function_calling "
            f"for {schema.__name__}"
        )
        return await _manual_parse(llm, schema, messages)

    # Fast path: providers that don't support json_schema (Anthropic,
    # OpenAI-compatible like DeepSeek/Alibaba/Together/xAI).
    # Go straight to function calling as the primary strategy.
    if _skip_json_schema(llm):
        logger.debug(
            f"Using function_calling as primary method for {type(llm).__name__} "
            f"(json_schema unsupported) — {schema.__name__}"
        )
        return await _function_calling_with_fallback(
            llm, schema, messages, fallback_to_manual_parse,
        )

    # Strategy 1: Try native structured output (json_schema) — most reliable
    # for providers that support it (OpenAI, Mistral, Google Gemini, etc.)
    try:
        logger.debug(f"Attempting structured output with method=json_schema for {schema.__name__}")
        structured_llm = llm.with_structured_output(schema, method="json_schema")
        result = await structured_llm.ainvoke(messages)

        if result is not None:
            _METRICS["json_schema_success"] += 1
            logger.debug(f"Successfully got structured output via json_schema for {schema.__name__}")
            return result

        _METRICS["json_schema_failure"] += 1
        logger.warning(f"json_schema returned None for {schema.__name__}, trying fallback")
    except Exception as e:
        _METRICS["json_schema_failure"] += 1
        logger.warning(f"json_schema failed for {schema.__name__}: {e}, trying fallback")

    # Strategy 2: Fall back to function calling.
    # We explicitly pass method="function_calling" because ChatOpenAI's
    # default changed to "json_schema" in langchain-openai >= 0.2, which
    # would make this strategy identical to Strategy 1 for OpenAI providers.
    try:
        logger.debug(f"Attempting structured output with function_calling for {schema.__name__}")
        structured_llm = llm.with_structured_output(schema, method="function_calling")
        result = await structured_llm.ainvoke(messages)

        if result is not None:
            _METRICS["default_method_success"] += 1
            logger.debug(f"Successfully got structured output via default method for {schema.__name__}")
            return result

        _METRICS["default_method_failure"] += 1
        logger.warning(f"Default method returned None for {schema.__name__}, trying manual parse")
    except Exception as e:
        _METRICS["default_method_failure"] += 1
        logger.warning(f"Default method failed for {schema.__name__}: {e}, trying manual parse")

    # Strategy 3: Manual parsing fallback
    if fallback_to_manual_parse:
        result = await _manual_parse(llm, schema, messages)
        if result is not None:
            return result

    # All strategies failed
    logger.error(f"All structured output strategies failed for {schema.__name__}")
    return None


async def _function_calling_with_fallback(
    llm: BaseChatModel,
    schema: Type[T],
    messages: List[BaseMessage],
    fallback_to_manual_parse: bool,
) -> Optional[T]:
    """Try function calling first, then fall back to manual parse.

    Used as the primary path for providers that don't support json_schema
    (Anthropic, DeepSeek, Alibaba, Together, xAI, etc.).
    """
    try:
        logger.debug(f"Attempting structured output with function_calling for {schema.__name__}")
        structured_llm = llm.with_structured_output(schema, method="function_calling")
        result = await structured_llm.ainvoke(messages)

        if result is not None:
            _METRICS["default_method_success"] += 1
            logger.debug(f"Successfully got structured output via function_calling for {schema.__name__}")
            return result

        _METRICS["default_method_failure"] += 1
        logger.warning(f"function_calling returned None for {schema.__name__}, trying manual parse")
    except Exception as e:
        _METRICS["default_method_failure"] += 1
        logger.warning(f"function_calling failed for {schema.__name__}: {e}, trying manual parse")

    if fallback_to_manual_parse:
        result = await _manual_parse(llm, schema, messages)
        if result is not None:
            return result

    logger.error(f"All structured output strategies failed for {schema.__name__}")
    return None


async def _manual_parse(
    llm: BaseChatModel,
    schema: Type[T],
    messages: List[BaseMessage],
) -> Optional[T]:
    """Get a raw LLM response and extract JSON matching *schema*."""
    try:
        logger.debug(f"Attempting manual JSON extraction for {schema.__name__}")

        raw_result = await llm.ainvoke(messages)
        raw_content = raw_result.content if hasattr(raw_result, 'content') else str(raw_result)

        parsed_data = _extract_json_from_text(raw_content)

        if parsed_data:
            result = schema(**parsed_data)
            _METRICS["manual_parse_success"] += 1
            logger.info(f"Successfully parsed {schema.__name__} via manual extraction")
            return result

        _METRICS["manual_parse_failure"] += 1
        logger.warning(f"Could not extract valid JSON for {schema.__name__} from raw response")
    except ValidationError as e:
        _METRICS["manual_parse_failure"] += 1
        logger.warning(f"Manual parse validation failed for {schema.__name__}: {e}")
    except Exception as e:
        _METRICS["manual_parse_failure"] += 1
        logger.warning(f"Manual parse failed for {schema.__name__}: {e}")

    return None


def reset_structured_output_metrics() -> None:
    """Reset all structured output metrics to zero."""
    for key in _METRICS:
        _METRICS[key] = 0


def get_structured_output_metrics() -> dict:
    """
    Get metrics about structured output success rates.

    Returns:
        Dictionary containing success/failure counts for each fallback tier
    """
    total = _METRICS["total_calls"]
    if total == 0:
        return _METRICS.copy()

    return {
        **_METRICS,
        "json_schema_success_rate": _METRICS["json_schema_success"] / total * 100,
        "default_method_success_rate": _METRICS["default_method_success"] / total * 100,
        "manual_parse_success_rate": _METRICS["manual_parse_success"] / total * 100,
        "overall_success_rate": (
            _METRICS["json_schema_success"] +
            _METRICS["default_method_success"] +
            _METRICS["manual_parse_success"]
        ) / total * 100,
    }


def _extract_json_from_text(text: str) -> Optional[dict]:
    """
    Attempts to extract a JSON object from text that may contain markdown,
    code blocks, or other formatting.

    Args:
        text: The text potentially containing JSON

    Returns:
        Parsed JSON dict, or None if extraction fails
    """
    # Strategy 1: Try to find JSON in code blocks (```json ... ```)
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # Strategy 2: Try to find any JSON object in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # Strategy 3: Try parsing the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return None
