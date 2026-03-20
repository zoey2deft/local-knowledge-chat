from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.services.embedding_service import generate_embedding

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "chunks.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


async def process_uploaded_text_file(file: UploadFile) -> dict[str, object]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    text = content.decode("utf-8").strip()
    if not text:
        raise ValueError("Uploaded file is empty")

    filename = file.filename or f"{uuid4()}.txt"
    raw_path = RAW_DIR / filename
    raw_path.write_bytes(content)

    chunks = split_text(text)
    chunk_records = []

    for index, chunk in enumerate(chunks):
        chunk_records.append(
            {
                "id": f"{filename}-{index}",
                "filename": filename,
                "chunk_index": index,
                "text": chunk,
                "embedding": generate_embedding(chunk),
            }
        )

    existing_records = load_chunks()
    existing_records.extend(chunk_records)
    PROCESSED_PATH.write_text(json.dumps(existing_records, indent=2), encoding="utf-8")

    return {"filename": filename, "chunks": len(chunk_records), "output": str(PROCESSED_PATH)}


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


def load_chunks() -> list[dict[str, object]]:
    if not PROCESSED_PATH.exists():
        return []

    data = json.loads(PROCESSED_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []

    return data
