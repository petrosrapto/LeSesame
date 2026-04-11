"""
Le Sésame Backend - Vector Memory Store

In-memory vector store backed by Mistral embeddings for
RAG-based guardian and adversarial levels.

Author: Petros Raptopoulos
Date: 2026/02/08
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .client import embed_texts, cosine_similarity

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    Lightweight in-memory vector store.

    Supports:
    - Adding texts with metadata
    - Semantic search via cosine similarity
    - Optional persistence to a JSON file
    """

    def __init__(self, persist_path: Optional[str] = None):
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self._persist_path = persist_path
        if persist_path:
            self._load(persist_path)

    # ── Add ──────────────────────────────────────────────────────────

    async def add(self, text: str, meta: Optional[Dict[str, Any]] = None):
        """Embed *text* and store it with optional *meta* data."""
        embs = await embed_texts([text])
        self.vectors.append(np.array(embs[0], dtype=np.float32))
        self.metadata.append({**(meta or {}), "text": text})
        if self._persist_path:
            self._save(self._persist_path)

    async def add_batch(self, texts: List[str], metas: Optional[List[Dict[str, Any]]] = None):
        """Embed and append a batch of texts."""
        if not texts:
            return
        embs = await embed_texts(texts)
        metas = metas or [{} for _ in texts]
        for text, emb, meta in zip(texts, embs, metas):
            self.vectors.append(np.array(emb, dtype=np.float32))
            self.metadata.append({**meta, "text": text})
        if self._persist_path:
            self._save(self._persist_path)

    # ── Search ───────────────────────────────────────────────────────

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return the *top_k* most similar entries to *query*."""
        if not self.vectors:
            return []
        q_emb = (await embed_texts([query]))[0]
        q_vec = np.array(q_emb, dtype=np.float32)
        scores = [
            float(np.dot(q_vec, v) / (np.linalg.norm(q_vec) * np.linalg.norm(v) + 1e-10))
            for v in self.vectors
        ]
        indices = np.argsort(scores)[::-1][:top_k]
        return [{"score": scores[i], **self.metadata[i]} for i in indices]

    # ── Persistence ──────────────────────────────────────────────────

    def _save(self, path: str):
        data = {
            "vectors": [v.tolist() for v in self.vectors],
            "metadata": self.metadata,
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def _load(self, path: str):
        p = Path(path)
        if not p.exists():
            return
        try:
            with open(p) as f:
                data = json.load(f)
            self.vectors = [np.array(v, dtype=np.float32) for v in data.get("vectors", [])]
            self.metadata = data.get("metadata", [])
            logger.info("VectorMemory loaded %d entries from %s", len(self.vectors), path)
        except Exception as exc:
            logger.warning("VectorMemory failed to load from %s: %s", path, exc)

    def __len__(self) -> int:
        return len(self.vectors)
