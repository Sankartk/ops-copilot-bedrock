from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    id: str
    source_file: str
    chunk_index: int
    text: str


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _chunk_markdown(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []

    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = p

    if buf:
        chunks.append(buf)

    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    out: List[str] = []
    prev_tail = ""
    for c in chunks:
        out.append((prev_tail + "\n\n" + c).strip() if prev_tail else c)
        prev_tail = c[-overlap:]
    return out


def ingest_markdown_dir(data_dir: str) -> List[Chunk]:
    rows: List[Chunk] = []
    md_files: List[str] = []

    for root, _, files in os.walk(data_dir):
        for fn in files:
            if fn.lower().endswith(".md"):
                md_files.append(os.path.join(root, fn))

    md_files.sort()

    for fp in md_files:
        text = _read_text(fp)
        rel = os.path.relpath(fp, data_dir).replace("\\", "/")
        for i, chunk in enumerate(_chunk_markdown(text)):
            rows.append(Chunk(id=f"{rel}:chunk{i}", source_file=rel, chunk_index=i, text=chunk))

    return rows
