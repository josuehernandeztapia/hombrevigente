"""
Staging de knowledge promotions — patrón CMU admin-knowledge-promote.ts.

El endpoint no toca FAQ/golden directamente; solo append a pending JSON.
`scripts/process_knowledge_promotions.py` aplica el batch y vacía entradas OK.
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

KbRoute = Literal["servicios", "longevity", "all"]
TargetSection = Literal["FAQ_PROMOTED"]

VALID_KB_ROUTES = ("servicios", "longevity", "all")
VALID_TARGET_SECTIONS = ("FAQ_PROMOTED",)


def _default_pending_path() -> Path:
    custom = os.getenv("HV_KNOWLEDGE_PENDING_PATH")
    if custom:
        return Path(custom)
    return Path(__file__).resolve().parent / "data" / "knowledge-promotions-pending.json"


def load_pending(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    pending_path = path or _default_pending_path()
    if not pending_path.exists():
        return []
    try:
        data = json.loads(pending_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_pending(items: List[Dict[str, Any]], path: Optional[Path] = None) -> None:
    pending_path = path or _default_pending_path()
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    pending_path.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _new_promo_id() -> str:
    suffix = secrets.token_hex(3)
    return f"promo-{int(datetime.now(timezone.utc).timestamp() * 1000)}-{suffix}"


def validate_promotion_fields(
    *,
    question: str,
    answer: str,
    kb_route: str = "longevity",
    target_section: str = "FAQ_PROMOTED",
) -> Optional[str]:
    q = (question or "").strip()
    a = (answer or "").strip()
    if len(q) < 5:
        return "question must be non-empty (>= 5 chars)"
    if len(a) < 5:
        return "answer must be non-empty (>= 5 chars)"
    if kb_route not in VALID_KB_ROUTES:
        return f"kb_route must be one of: {', '.join(VALID_KB_ROUTES)}"
    if target_section not in VALID_TARGET_SECTIONS:
        return f"target_section must be one of: {', '.join(VALID_TARGET_SECTIONS)}"
    return None


def submit_promotion(
    *,
    question: str,
    answer: str,
    kb_route: KbRoute = "longevity",
    target_section: TargetSection = "FAQ_PROMOTED",
    from_log_id: Optional[str] = None,
    notes: Optional[str] = None,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    err = validate_promotion_fields(
        question=question,
        answer=answer,
        kb_route=kb_route,
        target_section=target_section,
    )
    if err:
        return {"success": False, "error": err, "status_code": 400}

    pending = load_pending(path)
    log_id = (from_log_id or "").strip() or None
    if log_id:
        existing = next((p for p in pending if p.get("from_log_id") == log_id), None)
        if existing:
            return {
                "success": True,
                "idempotent": True,
                "message": "Promotion already submitted for this log_id",
                "promotion": existing,
                "total_pending": len(pending),
                "status_code": 200,
            }

    promotion: Dict[str, Any] = {
        "id": _new_promo_id(),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "submitted_by": "admin-pin",
        "question": question.strip(),
        "answer": answer.strip(),
        "kb_route": kb_route,
        "target_section": target_section,
    }
    if log_id:
        promotion["from_log_id"] = log_id
    if notes and notes.strip():
        promotion["notes"] = notes.strip()

    pending.append(promotion)
    save_pending(pending, path)

    return {
        "success": True,
        "promotion": promotion,
        "total_pending": len(pending),
        "next_steps": (
            "Run: python scripts/process_knowledge_promotions.py "
            "&& python scripts/sync_golden_set.py "
            "&& python embed_kb_local.py --source all"
        ),
        "status_code": 201,
    }


def remove_pending(promotion_id: str, path: Optional[Path] = None) -> Tuple[bool, int]:
    pending = load_pending(path)
    filtered = [p for p in pending if p.get("id") != promotion_id]
    if len(filtered) == len(pending):
        return False, len(pending)
    save_pending(filtered, path)
    return True, len(filtered)