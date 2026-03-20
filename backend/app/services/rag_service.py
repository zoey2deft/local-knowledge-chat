from __future__ import annotations

from typing import Any

from app.services.document_service import load_chunks
from app.services.embedding_service import generate_embedding
from app.services.llm_service import generate_response
from app.services.retrieval_service import retrieve_top_chunks

SYSTEM_INSTRUCTION = (
    "Answer the question using only the provided context. "
    "If the context is insufficient, say that clearly."
)


def answer_question(question: str) -> dict[str, Any]:
    chunks = load_chunks()
    if not chunks:
        return {
            "answer": "I don't have any indexed documents yet. Please upload a text file first.",
            "sources": [],
        }

    query_embedding = generate_embedding(question)
    top_chunks = retrieve_top_chunks(query_embedding, limit=3)

    context_sections = []
    for chunk in top_chunks:
        context_sections.append(
            f"[{chunk.get('id')}] {chunk.get('text', '')}"
        )

    context_text = "\n\n".join(context_sections)
    prompt = (
        f"Context:\n\n{context_text}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    answer = generate_response(prompt, system=SYSTEM_INSTRUCTION)

    sources = [
        {
            "source": chunk.get("filename"),
            "chunk_id": chunk.get("id"),
            "text_preview": _build_preview(str(chunk.get("text", ""))),
            "similarity": round(float(chunk.get("similarity", 0.0)), 4),
        }
        for chunk in top_chunks
    ]

    return {"answer": answer, "sources": sources}


def _build_preview(text: str, limit: int = 160) -> str:
    compact_text = " ".join(text.split())
    if len(compact_text) <= limit:
        return compact_text

    return f"{compact_text[:limit].rstrip()}..."
