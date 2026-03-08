from __future__ import annotations

import json
from typing import List, Optional

import boto3


class BedrockError(RuntimeError):
    pass


def _client(region: Optional[str] = None):
    return boto3.client("bedrock-runtime", region_name=region or "us-east-1")


def embed_titan(text: str, model_id: str = "amazon.titan-embed-text-v1", region: Optional[str] = None) -> List[float]:
    body = json.dumps({"inputText": text})
    br = _client(region)
    resp = br.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body,
    )
    payload = json.loads(resp["body"].read())
    emb = payload.get("embedding")
    if not emb:
        raise BedrockError(f"No embedding returned: {payload}")
    return emb


def converse_text(
    prompt: str,
    model_id: str,
    region: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> str:
    """Bedrock Converse helper for Nova / inference profiles."""
    br = _client(region)
    resp = br.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    content = resp.get("output", {}).get("message", {}).get("content", [])
    texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("text")]
    return "\n".join(texts).strip()
