"""
Le Sésame Backend - LangChain Embeddings Client

Wraps LangChain-compatible embeddings for semantic similarity computations.
Using LangChain embeddings ensures all calls are traced in LangSmith
alongside LLM calls.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import os
import logging
from typing import List

from langchain_community.utils.math import cosine_similarity as _matrix_cosine_similarity
from langchain_mistralai import MistralAIEmbeddings
from langsmith import traceable

logger = logging.getLogger(__name__)

_embeddings: MistralAIEmbeddings | None = None

EMBEDDING_MODEL = "mistral-embed"


def _get_embeddings() -> MistralAIEmbeddings:
    """Lazily initialise and return the MistralAIEmbeddings singleton."""
    global _embeddings
    if _embeddings is None:
        api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not api_key:
            try:
                from ...core import settings
                api_key = settings.mistral_api_key
            except Exception:
                pass
        _embeddings = MistralAIEmbeddings(
            model=EMBEDDING_MODEL,
            mistral_api_key=api_key,
        )
    return _embeddings


@traceable(run_type="embedding", name="embed_texts")
async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts using LangChain MistralAI embeddings.

    Decorated with @traceable so every call appears in LangSmith traces
    (LangChain Embeddings do not extend Runnable, so they are not
    auto-traced through the callback system like ChatModels are).

    Args:
        texts: A list of strings to embed.

    Returns:
        A list of embedding vectors (each a list of floats).
    """
    embeddings = _get_embeddings()
    return await embeddings.aembed_documents(texts)


@traceable(run_type="tool", name="cosine_similarity")
def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    return float(_matrix_cosine_similarity([a], [b])[0][0])
