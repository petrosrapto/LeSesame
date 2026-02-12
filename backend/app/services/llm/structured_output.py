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
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from .google import GemmaGoogleChatModel
from ...core import logger


def _is_manual_parse_only(llm: BaseChatModel) -> bool:
    """Return True for models that only support manual-parse structured output.

    Gemma models do not support JSON mode or native function calling through
    the Google Generative AI API.  Attempting ``with_structured_output`` on
    them wastes two API round-trips before falling to Strategy 3 anyway, so
    we short-circuit here.
    """
    return isinstance(llm, GemmaGoogleChatModel)


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

    # Fast path: models that only support manual parsing (e.g. Gemma)
    # Skip Strategies 1 & 2 to avoid wasted API calls and error noise.
    if _is_manual_parse_only(llm):
        logger.debug(
            f"Model only supports manual parse — skipping json_schema/function_calling "
            f"for {schema.__name__}"
        )
        return await _manual_parse(llm, schema, messages)

    # Strategy 1: Try native structured output (json_schema)
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

    # Strategy 2: Fall back to default method (function calling)
    try:
        logger.debug(f"Attempting structured output with default method for {schema.__name__}")
        structured_llm = llm.with_structured_output(schema)
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
