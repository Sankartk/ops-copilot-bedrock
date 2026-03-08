from __future__ import annotations

import os
from dataclasses import dataclass


def _get_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = (os.getenv(name) or str(default)).strip()
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    index_dir: str = "index"
    top_k: int = 4
    max_context_chars: int = 9000

    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # canonical provider name used everywhere
    llm_provider: str = "ollama"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # Bedrock
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    bedrock_inference_profile_arn: str = ""
    bedrock_max_tokens: int = 512
    bedrock_temperature: float = 0.2

    # back-compat aliases
    @property
    def llm_backend(self) -> str:
        return self.llm_provider

    @property
    def ollama_base_url(self) -> str:
        return self.ollama_host

    @classmethod
    def from_env(cls) -> "Settings":
        llm_provider = (os.getenv("LLM_PROVIDER") or os.getenv("LLM_BACKEND") or "ollama").strip().lower()
        ollama_host = (os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").strip()
        return cls(
            index_dir=(os.getenv("INDEX_DIR") or "index").strip(),
            top_k=_get_int("TOP_K", 4),
            max_context_chars=_get_int("MAX_CONTEXT_CHARS", 9000),
            embed_model=(os.getenv("EMBED_MODEL") or os.getenv("LOCAL_EMBED_MODEL") or "sentence-transformers/all-MiniLM-L6-v2").strip(),
            llm_provider=llm_provider,
            ollama_host=ollama_host,
            ollama_model=(os.getenv("OLLAMA_MODEL") or "llama3.2:3b").strip(),
            bedrock_region=(os.getenv("BEDROCK_REGION") or os.getenv("AWS_REGION") or "us-east-1").strip(),
            bedrock_model_id=(os.getenv("BEDROCK_MODEL_ID") or "amazon.nova-lite-v1:0").strip(),
            bedrock_inference_profile_arn=(os.getenv("BEDROCK_INFERENCE_PROFILE_ARN") or "").strip(),
            bedrock_max_tokens=_get_int("BEDROCK_MAX_TOKENS", 512),
            bedrock_temperature=_get_float("BEDROCK_TEMPERATURE", 0.2),
        )

    def safe_dump(self) -> str:
        return (
            f"index_dir: {self.index_dir}\n"
            f"top_k: {self.top_k}\n"
            f"max_context_chars: {self.max_context_chars}\n"
            f"embed_model: {self.embed_model}\n"
            f"llm_provider: {self.llm_provider}\n"
            f"ollama_host: {self.ollama_host}\n"
            f"ollama_model: {self.ollama_model}\n"
            f"bedrock_region: {self.bedrock_region}\n"
            f"bedrock_model_id: {self.bedrock_model_id}\n"
            f"bedrock_inference_profile_arn: {self.bedrock_inference_profile_arn}\n"
            f"bedrock_max_tokens: {self.bedrock_max_tokens}\n"
            f"bedrock_temperature: {self.bedrock_temperature}\n"
        )


settings = Settings.from_env()
