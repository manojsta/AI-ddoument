import httpx
from ..config import settings

def embed_text(text: str) -> list[float]:
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{settings.ollama_url}/api/embed",
                        json={"model": settings.embedding_model, "input": text})
        r.raise_for_status()
        try:
            data = r.json()
        except ValueError as exc:
            raise RuntimeError(f"Embedding service returned non-JSON (HTTP {r.status_code}): {r.text[:300]}") from exc
        vec = data.get("embeddings", [[]])[0]
        if len(vec) != 768:
            raise ValueError(f"Embedding dimension {len(vec)} does not match configured VECTOR(768). "
                             "Choose an embedding model/configuration that returns 768 dimensions or alter the DB schema.")
        return vec

def generate_answer(prompt: str) -> str:
    with httpx.Client(timeout=240) as client:
        r = client.post(f"{settings.ollama_url}/api/generate",
                        json={"model": settings.llm_model, "prompt": prompt, "stream": False})
        r.raise_for_status()
        try:
            payload = r.json()
        except ValueError as exc:
            raise RuntimeError(f"AI service returned non-JSON (HTTP {r.status_code}): {r.text[:300]}") from exc
        answer = payload.get("response", "").strip()
        if not answer:
            raise RuntimeError("AI service returned an empty response")
        return answer
