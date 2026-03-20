import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:1.5b"


def generate_response(prompt: str, system: str | None = None) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "system": system,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    content = data.get("response")
    if not isinstance(content, str):
        raise ValueError("Invalid response from Ollama")

    return content


def generate_chat_response(message: str) -> str:
    return generate_response(message)
