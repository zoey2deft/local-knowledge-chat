from __future__ import annotations

import math
from typing import Any

from app.services.document_service import load_chunks


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b) or not vector_a:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def retrieve_top_chunks(query_embedding: list[float], limit: int = 3) -> list[dict[str, Any]]:
    scored_chunks: list[dict[str, Any]] = []

    for chunk in load_chunks():
        embedding = chunk.get("embedding")
        if not isinstance(embedding, list):
            continue

        similarity = cosine_similarity(query_embedding, embedding)
        scored_chunk = dict(chunk)
        scored_chunk["similarity"] = similarity
        scored_chunks.append(scored_chunk)

    scored_chunks.sort(key=lambda item: item["similarity"], reverse=True)
    return scored_chunks[:limit]
