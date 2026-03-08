from __future__ import annotations

from typing import List, Optional, Dict, Any

from .config import settings
from .local_llm import generate as ollama_generate
from .query import RetrievalHit


def generate_answer(
    prompt: str,
    hits: Optional[List[RetrievalHit]] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    settings_override=None,
    backend: Optional[str] = None,
    **_: Dict[str, Any],
) -> str:
    """Backward-compatible generation wrapper.

    Supports callers that pass:
      - generate_answer(prompt, hits)
      - generate_answer(prompt, hits, model="...")
      - generate_answer(prompt=..., hits=..., backend=..., settings=...)
    """
    cfg = settings_override or settings
    chosen_provider = (provider or backend or getattr(cfg, "llm_provider", None) or getattr(cfg, "llm_backend", None) or "ollama").lower().strip()

    if chosen_provider == "bedrock":
        from .bedrock_client import converse_text
        model_id = model or getattr(cfg, "bedrock_inference_profile_arn", "") or getattr(cfg, "bedrock_model_id", "")
        if not model_id:
            raise RuntimeError("BEDROCK_MODEL_ID or BEDROCK_INFERENCE_PROFILE_ARN is not set")
        return converse_text(
            prompt=prompt,
            model_id=model_id,
            region=getattr(cfg, "bedrock_region", "us-east-1"),
            max_tokens=getattr(cfg, "bedrock_max_tokens", 512),
            temperature=getattr(cfg, "bedrock_temperature", 0.2),
        )

    base_url = getattr(cfg, "ollama_host", None) or getattr(cfg, "ollama_base_url", None) or "http://localhost:11434"
    chosen_model = model or getattr(cfg, "ollama_model", None) or "llama3.2:3b"
    return ollama_generate(prompt=prompt, base_url=base_url, model=chosen_model)
