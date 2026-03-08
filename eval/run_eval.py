# eval/run_eval.py
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure repo root is on sys.path so "import src" works when running eval\run_eval.py
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.embed_local import embed_text
from src.query import retrieve, build_prompt, filter_hits_by_query, RetrievalHit
from src.llm_generate import generate_answer


def load_cases(path: str = "eval/cases.json") -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def contains_required_terms(answer: str, required_terms: List[str]) -> List[str]:
    a = (answer or "").lower()
    missing = [t for t in required_terms if t.lower() not in a]
    return missing


def main():
    cases = load_cases()
    results: List[Dict[str, Any]] = []
    passed = 0

    for case in cases:
        case_id = case["id"]
        q = case["question"]
        required_terms = case.get("required_terms", [])

        q_emb = embed_text(q)
        hits, conf = retrieve(q, q_emb, index_dir="index", top_k=6)
        hits = filter_hits_by_query(q, hits)

        prompt, _context = build_prompt(q, hits, max_context_chars=9000)

        # NOTE: generate_answer accepts model= as keyword now (back-compat safe)
        ans = generate_answer(prompt, hits, model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"))

        missing = contains_required_terms(ans, required_terms)
        ok = (len(missing) == 0)

        results.append(
            {
                "id": case_id,
                "question": q,
                "confidence": conf,
                "pass": ok,
                "missing": missing,
                "answer": ans,
                "top_sources": [
                    {"source_file": h.source_file, "chunk_index": h.chunk_index, "score": h.score}
                    for h in hits[:3]
                ],
            }
        )

        passed += 1 if ok else 0

        print("=" * 90)
        print(f"CASE: {case_id}")
        print(f"Q: {q}")
        print(f"Confidence: {conf}")
        print(f"PASS: {ok} | Missing: {missing}")
        print("-" * 90)
        print(ans)

    out_path = Path("eval/eval_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n✅ Eval complete: {passed}/{len(cases)} passed")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()