"""
HV RAG API — POST/GET /rag/query + health check (Fly-ready).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
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
from traces import get_trace_stats, read_traces  # noqa: E402
from signal_detector import BetaSignalDetector  # noqa: E402
from action_handler import load_pending_actions, run_detect_and_act, get_proactive_health_trend  # noqa: E402
from feature_flags import list_active_flags, is_enabled  # noqa: E402  # Guía Capa 5
from whatsapp_channel import (  # noqa: E402
    beta_id_for_phone,
    twiml_empty,
    twiml_reply,
    validate_twilio_signature,
)

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

    # Fase 1: reportar el backend de estado operativo
    state_persistence = os.getenv("HV_STATE_PERSISTENCE", "files")
    postgres_state_ok = False
    try:
        from state_persistence import _is_postgres_available

        postgres_state_ok = _is_postgres_available()
    except Exception:
        pass

    ok = index_ok and beta_fixture_ok

    # Fase 5: señal de si hay señales proactivas pendientes (best effort, no bloquea)
    signal_count = 0
    try:
        detector = BetaSignalDetector()
        signal_count = len(detector.scan())
    except Exception:
        pass

    # Per Guía Agéntica: report strong opinion on SSOT
    ssot_postgres = state_persistence == "postgres" and postgres_state_ok
    ssot_status = "postgres" if ssot_postgres else state_persistence

    return {
        "status": "ok" if ok else "degraded",
        "index_loaded": index_ok,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "beta_states_dir": str(states_dir),
        "beta_states_writable": states_writable,
        "beta_fixture_row_0": beta_fixture_ok,
        "retrieval_backend": os.getenv("HV_RETRIEVAL_BACKEND", "json"),
        "state_persistence": state_persistence,
        "postgres_state_configured": postgres_state_ok,
        "traces_enabled": os.getenv("HV_TRACES_ENABLED", "true"),
        "pending_signals": signal_count,
        "pending_actions": len(load_pending_actions(limit=1000)),
        "ssot": ssot_status,
        "ssot_postgres_recommended": not ssot_postgres,
        "agent_status_endpoint": "/admin/agent_status (PIN)",
        "calibrate_endpoint": "/admin/calibrate (PIN, runs drift + baseline + health log)",
        "feature_flags": list_active_flags(),
        "feature_flags_note": "HV_FEATURE_XXX=false to disable (default ON). See feature_flags.py",
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


# ------------------------------------------------------------------
# Fase 3 — Admin traces (Capa 2 de la Guía Agéntica)
# 4 endpoints mínimos PIN-gated
# ------------------------------------------------------------------

@app.get("/admin/traces")
def admin_traces(
    limit: int = Query(50, ge=1, le=200),
    beta_id: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    errors_only: bool = Query(False),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    traces = read_traces(limit=limit, beta_id=beta_id, role=role, errors_only=errors_only)
    return {"count": len(traces), "traces": traces}


@app.get("/admin/traces/stats")
def admin_traces_stats(
    window_hours: int = Query(24, ge=1, le=720),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    stats = get_trace_stats(window_hours=window_hours)
    return stats


@app.get("/admin/traces/beta/{beta_id}")
def admin_traces_by_beta(
    beta_id: str,
    limit: int = Query(50, ge=1, le=200),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    traces = read_traces(limit=limit, beta_id=beta_id)
    return {"beta_id": beta_id, "count": len(traces), "traces": traces}


@app.get("/admin/traces/{trace_id}")
def admin_trace_by_id(
    trace_id: str,
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    # simple: buscamos por id (bigint como string)
    all_traces = read_traces(limit=1)  # ineficiente pero para MVP; en prod se haría query directa
    for t in all_traces:
        if str(t.get("id")) == str(trace_id):
            return t
    # fallback: intentar leer más
    more = read_traces(limit=200)
    for t in more:
        if str(t.get("id")) == str(trace_id):
            return t
    raise HTTPException(status_code=404, detail="trace not found")


# Fase 5/6 — Admin para señales proactivas + acciones (cierre del loop detectar -> actuar)
@app.get("/admin/signals")
def admin_signals(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    detector = BetaSignalDetector()
    signals = [s.to_dict() for s in detector.scan()]
    return {"count": len(signals), "signals": signals}


@app.get("/admin/pending_actions")
def admin_pending_actions(
    limit: int = Query(50, ge=1, le=200),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    actions = load_pending_actions(limit=limit)
    return {"count": len(actions), "actions": actions}


@app.post("/admin/signals/run")
def admin_run_detect_and_act(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    actions = run_detect_and_act()
    return {"count": len(actions), "actions": actions}


@app.post("/admin/pending_actions/execute")
def admin_execute_pending_actions(
    dry_run: bool = Query(False),
    beta_id: Optional[str] = Query(None),
    force: bool = Query(False, description="Bypass is_healthy gate (ops emergency only)"),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    from action_handler import execute_all_pending
    results = execute_all_pending(dry_run=dry_run, beta_id=beta_id, force=force)
    return {"executed_count": len(results), "actions": results}


@app.get("/admin/metrics")
def admin_metrics(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    from action_handler import compute_agent_metrics
    return compute_agent_metrics()


class IndiceLongevidadRequest(BaseModel):
    """Inputs para validar la metodología del Índice (uso interno, nivel A)."""
    labs: Optional[Dict[str, float]] = None
    wearable: Optional[Dict[str, float]] = None
    cuestionario: Optional[Dict[str, float]] = None


@app.post("/admin/indice/longevidad")
def admin_indice_longevidad(
    body: IndiceLongevidadRequest,
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    """
    Calcula el Vigente Longevidad para validar la metodología (NIVEL A — interno).
    Gated por admin PIN; NO se expone al beta ni se persiste en su estado. Promover a
    cara-al-usuario requiere flag + revisión COFEPRIS (ver docs/Metodologia_Indice_Vigente.md).
    """
    _require_admin_pin(pin, x_admin_pin)
    from indice_vigente import compute_indice_longevidad, headline_text
    r = compute_indice_longevidad(
        labs=body.labs, wearable=body.wearable, cuestionario=body.cuestionario
    )
    r["headline"] = headline_text(r)
    return r


@app.post("/admin/calibrate")
def admin_calibrate(
    sample: int = Query(0, ge=0, le=1000),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    # Dynamic import to avoid path issues (calibrate is in scripts/)
    import importlib.util
    from pathlib import Path
    _ROOT = Path(__file__).resolve().parent.parent
    cal_path = _ROOT / "scripts" / "calibrate_proactive.py"
    spec = importlib.util.spec_from_file_location("calibrate_proactive", cal_path)
    cal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cal)
    report = cal.run_calibration(sample_size=sample, use_json=False)
    # Log health as part of learning loop (Aprende)
    try:
        from action_handler import log_proactive_health_score
        log_proactive_health_score()
    except Exception:
        pass
    return {"status": "ok", "report": report}


@app.get("/admin/simulate")
def admin_simulate_proactive(
    beta_id: str = Query(...),
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    from action_handler import simulate_proactive_for_beta
    return simulate_proactive_for_beta(beta_id)


@app.get("/admin/agent_status")
def admin_agent_status(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)

    # Traces aggregates (últimas 24h por defecto)
    trace_stats = get_trace_stats(window_hours=24)

    # Proactive debt
    pending = load_pending_actions(limit=1000)
    pending_count = len([p for p in pending if p.get("status") == "pending"])

    # Last calibration (si existe)
    calibration = {}
    try:
        from pathlib import Path
        cal_path = Path("data/proactive_calibration.json")
        if cal_path.exists():
            calibration = json.loads(cal_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Last scheduled proactive run (from run_proactive_nightly.py)
    last_proactive_run = {}
    try:
        from pathlib import Path
        run_path = Path(os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions")) / "last_proactive_run.json"
        if run_path.exists():
            last_proactive_run = json.loads(run_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Proactive Health Score (new consolidated signal)
    health = {}
    try:
        from action_handler import compute_proactive_health_score
        health = compute_proactive_health_score()
    except Exception:
        health = {"score": None, "error": "could not compute"}

    # SSOT status
    ssot = {
        "mode": os.getenv("HV_STATE_PERSISTENCE", "files"),
        "postgres_configured": bool(os.getenv("HV_DATABASE_URL") or os.getenv("DATABASE_URL")),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "traces_24h": trace_stats,
        "proactive": {
            "pending_actions": pending_count,
            "last_calibration": {
                "calibrated_at": calibration.get("calibrated_at"),
                "total_triggered": calibration.get("summary", {}).get("total_triggered"),
                "drift": calibration.get("drift"),
            },
            "last_scheduled_run": last_proactive_run,
            "health_score": health,
            "health_trend": get_proactive_health_trend(limit=5),
        },
        "ssot": ssot,
        "feature_flags": list_active_flags(),
        "recommendations": [
            "Usa HV_STATE_PERSISTENCE=postgres en producción.",
            "Corre calibrate_proactive.py semanalmente.",
            "Revisa /admin/pending_actions y ejecútalos con el script correspondiente.",
            "Usa HV_FEATURE_XXX=false para deshabilitar branches (default ON, rollback <5s).",
        ],
    }


@app.get("/admin/betas")
def admin_betas(
    pin: str = Query(""),
    x_admin_pin: Optional[str] = Header(None, alias="x-admin-pin"),
):
    _require_admin_pin(pin, x_admin_pin)
    from state_persistence import list_all_betas
    from action_handler import load_pending_actions

    betas_raw = list_all_betas()
    pending = {a["beta_id"]: a for a in load_pending_actions(limit=500) if a.get("status") == "pending"}

    enriched = []
    for b in betas_raw:
        bid = b.get("beta_id")
        pending_action = pending.get(bid)
        enriched.append({
            "beta_id": bid,
            "phase": b.get("phase"),
            "next_action": b.get("next_action"),
            "progress": _compute_simple_progress(b.get("slots", {})),
            "last_active_at": b.get("last_active_at"),
            "turn_count": b.get("turn_count", 0),
            "pending_action": pending_action,
        })

    return {"count": len(enriched), "betas": enriched}


def _compute_simple_progress(slots: dict) -> float:
    if not slots:
        return 0.0
    done = sum(1 for v in slots.values() if v)
    return round(done / len(slots), 2)


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


# ------------------------------------------------------------------
# WhatsApp (Twilio) — webhook inbound: turn + last_active + concierge RAG
# ------------------------------------------------------------------

_WA_FALLBACK_REPLY = (
    "Recibido. En un momento te respondemos con calma — "
    "si es urgente, escribe 'humano' y te conectamos con el equipo."
)


def _twilio_public_url(request: Request) -> str:
    """Twilio firma la URL pública (https tras el proxy de Fly)."""
    url = str(request.url)
    proto = request.headers.get("x-forwarded-proto")
    if proto and url.startswith("http://") and proto == "https":
        url = "https://" + url[len("http://"):]
    return url


def _handle_inbound_media(beta_id: str, form: dict, num_media: int) -> Optional[str]:
    """
    Descarga el primer media soportado (PDF/imagen = estudio) e ingiere labs.
    Devuelve el texto de respuesta, o None si el media no es un estudio (deja que
    siga el flujo de texto). PII: el archivo se guarda en dir efímero por beta.
    """
    import tempfile
    from whatsapp_channel import (
        download_twilio_media, is_supported_labs_media, ChannelSendError,
    )
    from labs_ingest import ingest_labs_pdf

    for i in range(num_media):
        url = form.get(f"MediaUrl{i}", "")
        ctype = form.get(f"MediaContentType{i}", "")
        if not url or not is_supported_labs_media(ctype):
            continue
        try:
            dest_dir = os.path.join(
                os.getenv("HV_LABS_INBOX_DIR", tempfile.gettempdir()), beta_id
            )
            path = download_twilio_media(url, dest_dir, content_type=ctype,
                                         filename_stem=f"lab_{i}")
            result = ingest_labs_pdf(beta_id, path)
            return result.get("summary_text") or "Recibí tu estudio, gracias."
        except ChannelSendError as e:
            print(f"[wa-webhook] WARN media download {beta_id}: {e}")
            return ("Tu estudio llegó pero no pude descargarlo ahora; "
                    "el equipo lo revisará. 🙌")
        except Exception as e:
            print(f"[wa-webhook] WARN media ingest {beta_id}: {e}")
            return ("Recibí tu archivo pero no pude leerlo automáticamente; "
                    "el equipo lo revisa a mano.")
    return None  # ningún media soportado → seguir con el texto


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Inbound de Twilio (form-encoded). Efectos por mensaje:
    1. record_turn(channel='whatsapp') → bump de last_active_at (apaga señales
       de inactividad del lazo proactivo de forma natural).
    2. Respuesta concierge vía RAG (gates + confianza ya integrados en _run_query).
    Responde TwiML inline (no consume Messages API ni requiere template).
    """
    form = {k: str(v) for k, v in (await request.form()).items()}

    # Firma (fail-closed). HV_TWILIO_VALIDATE=false solo para dev/tests.
    if os.getenv("HV_TWILIO_VALIDATE", "true").strip().lower() not in ("false", "0", "no"):
        sig = request.headers.get("X-Twilio-Signature", "")
        if not validate_twilio_signature(_twilio_public_url(request), form, sig):
            raise HTTPException(status_code=403, detail="invalid twilio signature")

    from_phone = form.get("From", "")
    body = (form.get("Body") or "").strip()
    if not from_phone:
        return Response(content=twiml_empty(), media_type="application/xml")

    beta_id = beta_id_for_phone(from_phone)

    try:
        from state_manager import state_manager as _sm
        _sm.record_turn(beta_id, channel="whatsapp")
    except Exception as e:
        print(f"[wa-webhook] WARN record_turn({beta_id}): {e}")

    # Estudios (labs) por el hilo: si el beta adjunta un PDF/imagen, lo ingerimos
    # (parse → biomarcadores → slot labs_parseados). Gated por HV_FEATURE_WA_LABS.
    num_media = 0
    try:
        num_media = int(form.get("NumMedia", "0") or "0")
    except ValueError:
        num_media = 0
    if num_media > 0 and is_enabled("WA_LABS", default=True):
        media_reply = _handle_inbound_media(beta_id, form, num_media)
        if media_reply is not None:
            return Response(content=twiml_reply(media_reply), media_type="application/xml")

    if not body:
        return Response(content=twiml_empty(), media_type="application/xml")

    # Onboarding conversacional: si el beta es lead nuevo (sin intake) o está a media
    # conversación de onboarding, el guion determinístico conduce. Si ya tiene perfil,
    # pasa al concierge RAG. Gated por flag HV_FEATURE_WA_ONBOARDING (default ON).
    if is_enabled("WA_ONBOARDING", default=True):
        try:
            from onboarding_flow import (
                is_onboarding_active, should_start_onboarding, start_or_advance,
            )
            from state_persistence import load_state
            _state = load_state(beta_id)
            if is_onboarding_active(_state) or should_start_onboarding(_state):
                out = start_or_advance(beta_id, body)
                return Response(content=twiml_reply(out["reply"]), media_type="application/xml")
        except Exception as e:
            print(f"[wa-webhook] WARN onboarding flow for {beta_id}: {e}")

    reply = _WA_FALLBACK_REPLY
    try:
        res = _run_query(
            body, role="concierge", use_llm=True,
            beta_id=beta_id, channel="whatsapp",
        )
        ans = (res or {}).get("answer") or ""
        if ans.strip():
            reply = ans.strip()
    except Exception as e:
        print(f"[wa-webhook] WARN rag failed for {beta_id}: {e}")

    return Response(content=twiml_reply(reply), media_type="application/xml")


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