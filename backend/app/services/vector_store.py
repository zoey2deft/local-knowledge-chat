from __future__ import annotations

from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

BASE_DIR = Path(__file__).resolve().parents[2]
QDRANT_PATH = BASE_DIR / "data" / "qdrant"
COLLECTION_NAME = "knowledge_base"

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client

    if _client is None:
        QDRANT_PATH.mkdir(parents=True, exist_ok=True)
        _client = QdrantClient(path=str(QDRANT_PATH))

    return _client


def ensure_collection(vector_size: int) -> None:
    client = get_client()

    if client.collection_exists(COLLECTION_NAME):
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )


def upsert_chunks(chunks: list[dict[str, Any]]) -> None:
    if not chunks:
        return

    first_vector = chunks[0].get("vector")
    if not isinstance(first_vector, list) or not first_vector:
        raise ValueError("Cannot upsert chunks without a valid embedding vector")

    ensure_collection(len(first_vector))

    points = [
        models.PointStruct(
            id=str(chunk["id"]),
            vector=chunk["vector"],
            payload={
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
            },
        )
        for chunk in chunks
    ]

    get_client().upsert(collection_name=COLLECTION_NAME, points=points)


def search_similar_chunks(query_vector: list[float], limit: int = 3) -> list[dict[str, Any]]:
    if not query_vector:
        raise ValueError("Query embedding is empty")

    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        return []

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    results = []
    for hit in hits.points:
        payload = hit.payload or {}
        results.append(
            {
                "id": str(hit.id),
                "source": payload.get("source"),
                "chunk_id": payload.get("chunk_id"),
                "text": payload.get("text", ""),
                "similarity": float(hit.score),
            }
        )

    return results
