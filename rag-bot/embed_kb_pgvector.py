#!/usr/bin/env python3
"""
Sync knowledge base → Neon pgvector.

  python embed_kb_pgvector.py --migrate
  python embed_kb_pgvector.py --source all
  python embed_kb_pgvector.py --from-json knowledge_base/embeddings_local.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from kb_pipeline import load_all_chunks
from pgvector_retrieval import is_pgvector_configured, run_migration, sync_chunks_to_pgvector

load_dotenv()


def _chunks_from_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("chunks", [])


def main() -> int:
    parser = argparse.ArgumentParser(description="HV KB → pgvector (Neon)")
    parser.add_argument("--migrate", action="store_true", help="Aplicar 001_hv_kb_embeddings.sql")
    parser.add_argument("--migrate-only", action="store_true", help="Solo migración SQL")
    parser.add_argument("--source", choices=["servicios", "longevity", "all"], default="all")
    parser.add_argument(
        "--from-json",
        type=Path,
        help="Upsert desde índice JSON local (sin re-embed)",
    )
    parser.add_argument("--trigger", default="manual")
    args = parser.parse_args()

    if not is_pgvector_configured():
        print(
            "ERROR: DATABASE_URL/HV_DATABASE_URL debe ser postgres (Neon).",
            file=sys.stderr,
        )
        return 1

    if args.migrate or args.migrate_only:
        run_migration()
        print("Migration 001_hv_kb_embeddings.sql applied.")
    if args.migrate_only:
        return 0

    if args.from_json:
        chunks = _chunks_from_json(args.from_json)
    else:
        chunks = load_all_chunks(source=args.source)
        json_index = Path("knowledge_base/embeddings_local.json")
        if json_index.exists():
            by_id = {c["id"]: c for c in _chunks_from_json(json_index)}
            for chunk in chunks:
                prev = by_id.get(chunk["id"])
                if prev and prev.get("embedding"):
                    chunk["embedding"] = prev["embedding"]
                    chunk["content_hash"] = prev.get("content_hash", chunk.get("content_hash"))
        missing = [c for c in chunks if not c.get("embedding")]
        if missing:
            print(
                f"ERROR: {len(missing)} chunks sin embedding. "
                "Corre: python embed_kb_local.py --source all",
                file=sys.stderr,
            )
            return 1

    stats = sync_chunks_to_pgvector(chunks, trigger=args.trigger)
    print(
        f"pgvector sync: embedded={stats['embedded']} "
        f"skipped={stats['skipped']} total={stats['total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())