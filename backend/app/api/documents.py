from fastapi import APIRouter, File, HTTPException, UploadFile
import requests

from app.services.document_service import process_uploaded_text_file

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    try:
        result = await process_uploaded_text_file(file)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Failed to reach Ollama embeddings API") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
