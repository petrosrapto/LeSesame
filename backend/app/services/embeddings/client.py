"""
Le Sésame Backend - Mistral Embeddings Client

Wraps the Mistral embeddings API for semantic similarity computations.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import os
import logging
from typing import List

import numpy as np
from mistralai import Mistral

logger = logging.getLogger(__name__)

_client: Mistral | None = None

EMBEDDING_MODEL = "mistral-embed"


def _get_client() -> Mistral:
    """Lazily initialise and return the Mistral client singleton."""
    global _client
    if _client is None:
        api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not api_key:
            # Fall back to settings
            try:
                from ...core import settings
                api_key = settings.mistral_api_key
            except Exception:
                pass
        _client = Mistral(api_key=api_key)
    return _client


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts using Mistral's embedding model.

    Args:
        texts: A list of strings to embed.

    Returns:
        A list of embedding vectors (each a list of floats).
    """
    client = _get_client()
    # Mistral batch limit is 16384 tokens / ~50 texts; chunk if needed.
    all_embeddings: List[List[float]] = []
    batch_size = 32
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, inputs=batch)
        all_embeddings.extend([d.embedding for d in resp.data])
    return all_embeddings


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom < 1e-10:
        return 0.0
    return float(np.dot(va, vb) / denom)
