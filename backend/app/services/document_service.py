from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.services.embedding_service import generate_embedding
from app.services.vector_store import upsert_chunks

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


async def process_uploaded_text_file(file: UploadFile) -> dict[str, object]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    text = content.decode("utf-8").strip()
    if not text:
        raise ValueError("Uploaded file is empty")

    filename = file.filename or f"{uuid4()}.txt"
    raw_path = RAW_DIR / filename
    raw_path.write_bytes(content)

    chunks = split_text(text)
    if not chunks:
        raise ValueError("No valid text chunks were generated from the uploaded file")

    chunk_records = []
    for index, chunk in enumerate(chunks):
        chunk_records.append(
            {
                "id": str(uuid4()),
                "chunk_id": f"{filename}-{index}",
                "source": filename,
                "text": chunk,
                "vector": generate_embedding(chunk),
            }
        )

    upsert_chunks(chunk_records)

    return {"filename": filename, "chunks": len(chunk_records), "output": str(raw_path)}


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size")

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks
