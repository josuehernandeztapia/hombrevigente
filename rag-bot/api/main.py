"""
HV RAG API — POST/GET /rag/query + health check (Fly-ready).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# Cargar .env desde rag-bot/ aunque uvicorn arranque desde api/
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

import sys

sys.path.insert(0, str(_ROOT))

from knowledge_gap_detector import detect_knowledge_gaps, render_gaps_report
from knowledge_promote import load_pending, remove_pending, submit_promotion
from newsletter_approval_dispatch import dispatch_pulso_approval
from newsletter_approval_token import verify_token
from rag_retrieval_local import rag_query_local  # noqa: E402

app = FastAPI(
    title="Hombre Vigente RAG API",
    version="1.0.0",
    description="Motor RAG local con gates HV, confianza y rol concierge MVP-0",
)

_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RagQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    role: Literal["default", "concierge"] = "default"
    route: Optional[Literal["servicios", "longevity", "all"]] = None
    use_llm: bool = True
    top_k: int = Field(5, ge=1, le=10)
    avenida_max: Literal["1", "2", "1-2"] = "1"
    beta_id: Optional[str] = Field(
        None,
        max_length=64,
        description="row-0, caso0, tally-{id} — carga intake congelado",
    )
    channel: Optional[Literal["whatsapp", "api", "cli", "notas", "tally", "email"]] = "api"


class KnowledgePromoteRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    answer: str = Field(..., min_length=5, max_length=8000)
    kb_route: Literal["servicios", "longevity", "all"] = "longevity"
    target_section: Literal["FAQ_PROMOTED"] = "FAQ_PROMOTED"
    from_log_id: Optional[str] = Field(None, max_length=64)
    notes: Optional[str] = Field(None, max_length=2000)


def _run_query(
    query: str,
    *,
    role: str = "default",
    route: Optional[str] = None,
    use_llm: bool = True,
    top_k: int = 5,
    avenida_max: str = "1",
    parse: bool = False,
    beta_id: Optional[str] = None,
    channel: Optional[str] = "api",
) -> dict:
    index_path = Path(
        os.getenv("HV_EMBEDDINGS_INDEX", str(_ROOT / "knowledge_base" / "embeddings_local.json"))
    )
    if not index_path.is_absolute():
        index_path = _ROOT / index_path
    if not index_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Index missing. Run: python embed_kb_local.py --source all",
        )
    try:
        return rag_query_local(
            query,
            index_path=index_path,
            kb_route=route,
            top_k=top_k,
            avenida_max=avenida_max,
            use_llm=use_llm and bool(os.getenv("OPENAI_API_KEY")),
            role=role,
            parse=parse,
            source="api",
            beta_id=beta_id,
            channel=channel,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/health")
def health():
    from frozen_context import resolve_intake

    idx = Path(
        os.getenv("HV_EMBEDDINGS_INDEX", str(_ROOT / "knowledge_base" / "embeddings_local.json"))
    )
    if not idx.is_absolute():
        idx = _ROOT / idx
    index_ok = idx.exists()

    states_dir = Path(os.getenv("HV_BETA_STATES_DIR", "data/beta_states"))
    if not states_dir.is_absolute():
        states_dir = _ROOT / states_dir
    states_writable = states_dir.exists() and os.access(states_dir, os.W_OK)

    intake, _ = resolve_intake(beta_id="row-0")
    beta_fixture_ok = intake is not None

    ok = index_ok and beta_fixture_ok
    return {
        "status": "ok" if ok else "degraded",
        "index_loaded": index_ok,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "beta_states_dir": str(states_dir),
        "beta_states_writable": states_writable,
        "beta_fixture_row_0": beta_fixture_ok,
        "retrieval_backend": os.getenv("HV_RETRIEVAL_BACKEND", "json"),
    }


@app.post("/rag/query")
def rag_query_post(body: RagQueryRequest, parse: bool = Query(False)):
    return _run_query(
        body.query,
        role=body.role,
        route=body.route,
        use_llm=body.use_llm,
        top_k=body.top_k,
        avenida_max=body.avenida_max,
        parse=parse,
        beta_id=body.beta_id,
        channel=body.channel,
    )


def _resolve_admin_pin(pin: str, x_admin_pin: Optional[str]) -> str:
    return (x_admin_pin or pin or "").strip()


def _admin_pin_ok(pin: str) -> bool:
    expected = os.getenv("HV_ADMIN_PIN", "")
    if not expected:
        return os.getenv("ENVIRONMENT", "development") != "production"
    return pin == expected


def _require_admin_pin(pin: str, x_admin_pin: Optional[str] = None) -> None:
    if not _admin_pin_ok(_resolve_admin_pin(pin, x_admin_pin)):
        raise HTTPException(status_code=401, detail="invalid or missing pin")


@app.get("/admin/knowledge/gaps")
def knowledge_gaps(
    days: int = Query(7, ge=1, le=90),
    threshold: Optional[float] = Query(None),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    gaps = detect_knowledge_gaps(days=days, gap_threshold=threshold)
    return {
        "days": days,
        "threshold": threshold,
        "count": len(gaps),
        "gaps": gaps,
        "report_md": render_gaps_report(
            gaps,
            days=days,
            threshold=threshold or float(os.getenv("HV_COSINE_MIN", "0.55")),
        ),
    }


@app.post("/admin/knowledge/promote")
def knowledge_promote(
    body: KnowledgePromoteRequest,
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    result = submit_promotion(
        question=body.question,
        answer=body.answer,
        kb_route=body.kb_route,
        target_section=body.target_section,
        from_log_id=body.from_log_id,
        notes=body.notes,
    )
    if not result.get("success"):
        raise HTTPException(status_code=result.get("status_code", 400), detail=result.get("error"))
    status_code = result.pop("status_code", 201)
    return JSONResponse(content=result, status_code=status_code)


@app.get("/admin/knowledge/pending")
def knowledge_pending(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    pending = load_pending()
    return {"count": len(pending), "promotions": pending}


@app.delete("/admin/knowledge/pending/{promotion_id}")
def knowledge_pending_delete(
    promotion_id: str,
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    removed, remaining = remove_pending(promotion_id)
    if not removed:
        raise HTTPException(status_code=404, detail="promotion not found")
    return {"success": True, "removed_id": promotion_id, "remaining": remaining}


def _approval_page(ok: bool, message: str) -> str:
    color = "#2d6a4f" if ok else "#9b2226"
    title = "Pulso Vigente" if ok else "No se pudo aprobar"
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="font-family:system-ui,sans-serif;max-width:520px;margin:48px auto;padding:24px;color:#1a1a1a;">
  <h1 style="color:{color};font-size:1.4rem;">{title}</h1>
  <p>{message}</p>
  <p style="font-size:0.85rem;color:#666;">Hombre Vigente™ · Pulso Vigente</p>
</body></html>"""


@app.get("/newsletter/approve", response_class=HTMLResponse)
def newsletter_approve(
    issue: str = Query(..., min_length=5, max_length=256),
    action: str = Query("approve"),
    token: str = Query(..., min_length=10),
):
    issue_path = issue.strip()
    if action not in ("approve", "revise"):
        return HTMLResponse(_approval_page(False, "Acción no válida."), status_code=400)
    if not verify_token(issue_path, action, token):
        return HTMLResponse(
            _approval_page(
                False,
                "Enlace inválido o expirado. Abre el issue de GitHub o pide un nuevo borrador por correo.",
            ),
            status_code=403,
        )
    result = dispatch_pulso_approval(issue_path, action)
    if not result.get("ok"):
        return HTMLResponse(
            _approval_page(False, result.get("error", "Error al procesar la aprobación.")),
            status_code=502,
        )
    if action == "approve":
        msg = "Aprobación recibida. El envío a audiencia Plus se procesará en unos minutos."
    else:
        msg = "Solicitud de cambios recibida. Recibirás un nuevo borrador por correo."
    return HTMLResponse(_approval_page(True, msg))


@app.get("/rag/query")
def rag_query_get(
    q: str = Query(..., min_length=1, max_length=2000),
    role: Literal["default", "concierge"] = "default",
    route: Optional[Literal["servicios", "longevity", "all"]] = None,
    use_llm: bool = True,
    top_k: int = Query(5, ge=1, le=10),
    avenida_max: Literal["1", "2", "1-2"] = "1",
    parse: bool = Query(False),
    beta_id: Optional[str] = Query(None, max_length=64),
    channel: Optional[str] = Query("api"),
):
    return _run_query(
        q,
        role=role,
        route=route,
        use_llm=use_llm,
        top_k=top_k,
        avenida_max=avenida_max,
        parse=parse,
        beta_id=beta_id,
        channel=channel,
    )