from __future__ import annotations

import json
import requests


class OllamaError(RuntimeError):
    pass


def generate(prompt: str, base_url: str, model: str, timeout_s: int = 120) -> str:
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        r = requests.post(url, json=payload, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()
        return (data.get("response") or "").strip()
    except requests.RequestException as e:
        raise OllamaError(f"Ollama request failed: {e}") from e
    except json.JSONDecodeError as e:
        raise OllamaError("Ollama returned non-JSON response") from e