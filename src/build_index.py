from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, List, Tuple

import faiss
import numpy as np

from .embed_local import embed_text


def read_markdown_files(data_dir: str) -> List[Tuple[str, str]]:
    docs: List[Tuple[str, str]] = []
    for name in os.listdir(data_dir):
        if name.lower().endswith(".md"):
            path = os.path.join(data_dir, name)
            with open(path, "r", encoding="utf-8") as f:
                docs.append((name, f.read()))
    if not docs:
        raise RuntimeError(f"No .md files found in {data_dir}")
    return docs


def chunk_text(text: str, chunk_chars: int = 1200, overlap_chars: int = 200) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + chunk_chars)
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(chunk)
        i = max(j - overlap_chars, j)
    return chunks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data", help="Folder with markdown runbooks")
    ap.add_argument("--index-dir", default="index", help="Output folder for FAISS index + metadata")
    ap.add_argument("--chunk-chars", type=int, default=1200)
    ap.add_argument("--overlap-chars", type=int, default=200)
    ap.add_argument("--sleep", type=float, default=0.0, help="Delay between embeddings (local usually 0)")
    args = ap.parse_args()

    os.makedirs(args.index_dir, exist_ok=True)

    docs = read_markdown_files(args.data_dir)

    rows: List[Dict] = []
    vectors: List[List[float]] = []

    for filename, content in docs:
        chunks = chunk_text(content, args.chunk_chars, args.overlap_chars)
        for idx, chunk in enumerate(chunks):
            emb = embed_text(chunk)
            vectors.append(emb)
            rows.append(
                {
                    "id": f"{filename}::chunk{idx}",
                    "source_file": filename,
                    "chunk_index": idx,
                    "text": chunk,
                }
            )
            if args.sleep:
                time.sleep(args.sleep)

    X = np.array(vectors, dtype="float32")
    faiss.normalize_L2(X)
    dim = X.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(X)

    faiss.write_index(index, os.path.join(args.index_dir, "faiss.index"))
    with open(os.path.join(args.index_dir, "docs.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f" Indexed {len(rows)} chunks from {len(docs)} files -> {args.index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())