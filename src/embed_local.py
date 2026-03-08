from __future__ import annotations

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _get_model(name: str) -> SentenceTransformer:
    return SentenceTransformer(name)


def embed_text(text: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    """Returns a normalized embedding vector (list[float]) for a single text."""
    m = _get_model(model_name)
    v = m.encode([text], normalize_embeddings=True)
    return v[0].tolist()
