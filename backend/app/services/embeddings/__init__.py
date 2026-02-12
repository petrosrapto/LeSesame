"""
Le Sésame Backend - Embeddings Module

Provides Mistral embedding utilities and an in-memory vector store
for RAG-based guardian and adversarial levels.
"""

from .client import embed_texts, cosine_similarity
from .memory import VectorMemory

__all__ = [
    "embed_texts",
    "cosine_similarity",
    "VectorMemory",
]
