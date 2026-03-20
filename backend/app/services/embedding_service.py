import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    embedding = data.get("embedding")
    if not isinstance(embedding, list):
        raise ValueError("Invalid embedding response from Ollama")

    return embedding
