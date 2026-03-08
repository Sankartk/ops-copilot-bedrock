from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import faiss
import numpy as np


@dataclass
class RetrievalHit:
    id: str
    source_file: str
    chunk_index: int
    text: str
    score: float


RetrievedChunk = RetrievalHit


def _load_index(index_dir: str):
    index_path = os.path.join(index_dir, "faiss.index")
    docs_path = os.path.join(index_dir, "docs.json")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Missing FAISS index: {index_path}")
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Missing docs.json: {docs_path}")

    index = faiss.read_index(index_path)
    with open(docs_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    return index, rows


def _to_float32_unit(vec: List[float]) -> np.ndarray:
    v = np.asarray(vec, dtype="float32").reshape(-1)
    n = np.linalg.norm(v)
    return (v / n) if n > 0 else v


def _confidence_from_scores(scores: List[float]) -> int:
    if not scores:
        return 0
    top1 = float(scores[0])
    top2 = float(scores[1]) if len(scores) > 1 else (top1 - 0.2)
    base = (top1 - 0.20) / (0.90 - 0.20)
    base = max(0.0, min(1.0, base)) * 85.0
    gap = max(0.0, top1 - top2)
    bonus = max(0.0, min(15.0, gap * 100.0))
    return int(round(min(100.0, base + bonus)))


def retrieve(query: str, query_embedding: List[float], index_dir: str = "index", top_k: int = 4) -> Tuple[List[RetrievalHit], int]:
    index, rows = _load_index(index_dir)
    q = _to_float32_unit(query_embedding).reshape(1, -1)
    scores, ids = index.search(q, top_k)
    scores_list = [float(s) for s in scores[0] if s != -1e9]
    conf = _confidence_from_scores(scores_list)

    hits: List[RetrievalHit] = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        row = rows[int(idx)]
        hits.append(
            RetrievalHit(
                id=row.get("id", f"row{idx}"),
                source_file=row.get("source_file", "unknown"),
                chunk_index=int(row.get("chunk_index", -1)),
                text=row.get("text", ""),
                score=float(score),
            )
        )
    return hits, conf


def format_sources_markdown(hits: List[RetrievalHit]) -> str:
    if not hits:
        return "_No sources retrieved._"
    blocks = []
    for i, h in enumerate(hits, start=1):
        blocks.append(
            f"**Source {i}** — `{h.source_file}` (chunk {h.chunk_index}, score {h.score:.3f})\n\n"
            f"```text\n{h.text.strip()}\n```"
        )
    return "\n\n---\n\n".join(blocks)


def _detect_topic(question: str) -> str:
    q = (question or "").lower()
    if any(k in q for k in ["rds", "aurora", "postgres", "mysql", "dbload", "connections", "databaseconnections", "cpu"]):
        return "rds"
    if any(k in q for k in ["alb", "load balancer", "target group", "5xx", "httpcode_elb_5xx"]):
        return "alb"
    if any(k in q for k in ["ecs", "task definition", "deploy", "deployment", "rollback"]):
        return "ecs"
    return "general"


_TOPIC_TERMS = {
    "rds": ["rds", "aurora", "postgres", "mysql", "pg_stat_activity", "performance insights", "connections", "databaseconnections", "slow query", "slow queries", "dbload", "cloudwatch"],
    "alb": ["alb", "load balancer", "target group", "5xx", "healthyhostcount", "targetresponsetime", "httpcode_elb_5xx", "cloudwatch"],
    "ecs": ["ecs", "task", "service", "task definition", "deployment", "rollback", "update-service", "force-new-deployment"],
}


def filter_hits_by_query(question: str, hits: List[RetrievalHit]) -> List[RetrievalHit]:
    if not hits:
        return hits
    topic = _detect_topic(question)
    terms = _TOPIC_TERMS.get(topic, [])
    if not terms:
        return hits[:2]
    filtered = [h for h in hits if any(t in (h.text or "").lower() for t in terms)]
    return filtered if filtered else hits[:2]


def build_prompt(question: str, hits: List[RetrievalHit], max_context_chars: int = 9000) -> tuple[str, str]:
    if not hits:
        return (
            "You are an Ops runbook assistant.\n"
            "No runbook context was retrieved.\n"
            'Respond exactly with: I could not find this in the runbooks.\n\n'
            f"Question: {question}\n",
            "",
        )

    hits = filter_hits_by_query(question, hits)

    total = 0
    ctx_parts = []
    for i, h in enumerate(hits, start=1):
        block = (
            f"CITE:[Source {i}] file={h.source_file} chunk={h.chunk_index} score={h.score:.4f}\n"
            f"{h.text.strip()}\n\n"
        )
        if total + len(block) > max_context_chars and ctx_parts:
            break
        ctx_parts.append(block)
        total += len(block)

    context = "".join(ctx_parts)
    
    topic = _detect_topic(question)
    required_hint = ""
    if topic == "rds":
        required_hint = (
            "REQUIRED WORDING RULES:\n"
            "- If the context mentions slow query or slow query logs, you MUST include the exact phrase 'slow queries' in the answer.\n"
            "- If the context mentions connections or DatabaseConnections, you MUST include the exact word 'connections' in the answer.\n"
            "- If the context mentions CloudWatch, you MUST include the exact word 'CloudWatch' in the answer.\n"
            "- Keep the answer focused on RDS only.\n"
        )
    elif topic == "alb":
        required_hint = (
            "REQUIRED WORDING RULES:\n"
            "- If the context mentions CloudWatch, you MUST include the exact word 'CloudWatch' in the answer.\n"
            "- Keep the answer focused on ALB only.\n"
        )
    prompt = f"""You are Ops Copilot, a DevOps runbook assistant.

STRICT RULES:
- Use ONLY the provided runbook context.
- Do NOT invent metrics/commands/resources not in context.
- Every checklist item MUST end with a citation like [Source 1].
- Do NOT answer a different question than the one asked.
- Every metric/log/query/command MUST include [Source 1] style citations.
- NEVER output [Source N], [Source 0], or any placeholder. Use only citations that exist in the context below.
- If context is insufficient, respond exactly: "I could not find this in the runbooks."

{required_hint}
OUTPUT FORMAT (use these headings exactly):

Summary:
<1-2 lines, include at least one citation>

Triage checklist:
- Step ... [Source 1]
- Step ... [Source 1]

Runbook signals:
- Metrics: ... [Source 1]
- Logs: ... [Source 1]
- Dashboards: ... [Source 1] (or "None in context" [Source 1])
- SQL/Queries: ... [Source 1]
- Commands: ... [Source 1]

Answer:
<short, actionable answer, include citations>

Question:
{question}

Runbook context:
{context}
"""
    return prompt, context
