from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

from app.services.rag_service import answer_question

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, object]:
    try:
        response = answer_question(payload.message)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Failed to reach Ollama") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return response
