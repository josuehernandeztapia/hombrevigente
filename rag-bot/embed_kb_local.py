#!/usr/bin/env python3
"""
Genera embeddings locales (JSON) para RAG sin Pinecone.
Embed diferencial: solo chunks cuyo content_hash cambió.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from kb_pipeline import load_all_chunks

load_dotenv()

DEFAULT_OUTPUT = Path("knowledge_base/embeddings_local.json")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


def _load_existing(path: Path) -> Dict:
    if not path.exists():
        return {"chunks": []}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _embed_batch(client, texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
    )
    return [item.embedding for item in response.data]


def build_embeddings(
    source: str = "all",
    output: Path = DEFAULT_OUTPUT,
    base_path: Path = Path("."),
    force: bool = False,
) -> Dict:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("pip install openai python-dotenv") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY no configurada en .env")

    client = OpenAI(api_key=api_key)
    chunks = load_all_chunks(source=source, base_path=base_path)
    existing = _load_existing(output)
    by_id = {c["id"]: c for c in existing.get("chunks", [])}

    to_embed = []
    reused = 0
    for chunk in chunks:
        prev = by_id.get(chunk["id"])
        if not force and prev and prev.get("content_hash") == chunk["content_hash"]:
            chunk["embedding"] = prev["embedding"]
            reused += 1
        else:
            to_embed.append(chunk)

    print(f"📦 Chunks totales: {len(chunks)} | reutilizados: {reused} | a embeddar: {len(to_embed)}")

    batch_size = 64
    for i in range(0, len(to_embed), batch_size):
        batch = to_embed[i : i + batch_size]
        texts = [c["text"][:8000] for c in batch]
        embeddings = _embed_batch(client, texts)
        for chunk, emb in zip(batch, embeddings):
            chunk["embedding"] = emb
        if i + batch_size < len(to_embed):
            time.sleep(0.3)

    out = {
        "version": 1,
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIMS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "stats": {
            "total_chunks": len(chunks),
            "embedded_new": len(to_embed),
            "reused": reused,
        },
        "chunks": chunks,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    print(f"✅ Guardado: {output} ({len(chunks)} chunks)")
    return out


def main():
    parser = argparse.ArgumentParser(description="Embeddings locales JSON (sin Pinecone)")
    parser.add_argument("--source", choices=["servicios", "longevity", "all"], default="all")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Re-embeber todo")
    args = parser.parse_args()
    build_embeddings(source=args.source, output=args.output, force=args.force)


if __name__ == "__main__":
    main()