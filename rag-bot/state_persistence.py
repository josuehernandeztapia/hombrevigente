"""
State Persistence Layer — Fase 1 de alineación con Guía Agéntica Estándar.

Soporta:
- HV_STATE_PERSISTENCE=files (default, comportamiento actual)
- HV_STATE_PERSISTENCE=postgres (SSOT en hv_beta_states)
- HV_STATE_PERSISTENCE=dual (escribe a ambos durante transición)

Política de lectura (aclarada):
- Cuando el backend primario es postgres y está configurado: leer SIEMPRE de Postgres.
- Fallback a archivos SOLO en error de lectura (degradación explícita + warning).
- Postgres gana siempre como fuente de verdad una vez activado.

Slots: se persisten tal cual en state_data (derivan en sync_from_intake o vía fill_slot futuro).
turn_number: se denormaliza en state_data. El SSOT atómico vendrá de hv_agent_traces (ver next_turn_number).

Incluye manejo básico de state_version (optimistic lock) y last_active_at.
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Reutilizamos el patrón de conexión ya probado en pgvector_retrieval.py
try:
    from pgvector_retrieval import database_url as _pgvector_database_url
    from pgvector_retrieval import is_pgvector_configured as _is_pgvector_configured
except Exception:
    _pgvector_database_url = None
    _is_pgvector_configured = None


class StateVersionConflictError(Exception):
    """Se lanza cuando el optimistic lock falla (UPDATE 0 rows). El caller debe reintentar 1x como máximo."""
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persistence_mode() -> str:
    """files | postgres | dual

    Per Guía Agéntica: Postgres is the only source of truth (SSOT).
    If a Postgres DATABASE_URL/HV_DATABASE_URL is present, we strongly prefer
    "postgres" mode. "files" is only for pure local dev without DB.
    """
    raw = os.getenv("HV_STATE_PERSISTENCE", "").strip().lower()

    # Explicit override takes precedence
    if raw in ("postgres", "pg", "db", "neon"):
        return "postgres"
    if raw in ("dual", "both", "files+postgres"):
        return "dual"
    if raw == "files":
        return "files"

    # Smart default: if we have a real Postgres URL, use it as SSOT
    url = _get_database_url()
    if url and "postgres" in url:
        return "postgres"

    # Last resort: files (dev without DB)
    return "files"


def _states_dir() -> Path:
    raw = os.getenv("HV_BETA_STATES_DIR", "data/beta_states")
    return Path(raw)


def _file_path(beta_id: str) -> Path:
    return _states_dir() / f"{beta_id}.json"


def _is_postgres_available() -> bool:
    if _is_pgvector_configured is not None:
        return _is_pgvector_configured()
    # Fallback manual
    url = _get_database_url()
    return bool(url and "postgres" in url)


def _get_database_url() -> Optional[str]:
    if _pgvector_database_url is not None:
        return _pgvector_database_url()
    url = os.getenv("HV_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    url = url.strip()
    if not url or url.startswith("sqlite"):
        return None
    if "postgres" not in url:
        return None
    return url


@contextmanager
def _connection():
    """Mismo patrón que pgvector_retrieval.py"""
    import psycopg
    url = _get_database_url()
    if not url:
        raise RuntimeError("HV_DATABASE_URL / DATABASE_URL postgres no configurada")
    conn = psycopg.connect(url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ------------------------------------------------------------------
# Archivos (modo legacy / fallback / dual)
# ------------------------------------------------------------------

def _load_from_file(beta_id: str) -> Optional[Dict[str, Any]]:
    dest = _file_path(beta_id)
    if not dest.exists():
        return None
    data = json.loads(dest.read_text(encoding="utf-8"))
    return data


def _save_to_file(beta_id: str, state: Dict[str, Any]) -> None:
    dest = _file_path(beta_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    state = dict(state)  # copia
    state["updated_at"] = _utc_now()
    dest.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------
# Postgres (SSOT cuando está activado)
# ------------------------------------------------------------------

def _load_from_postgres(beta_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT state_data, state_version
        FROM hv_beta_states
        WHERE beta_id = %s
    """
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (beta_id,))
            row = cur.fetchone()
            if not row:
                return None
            state = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            # Adjuntamos la versión actual para que el caller pueda usarla en updates
            state["_state_version"] = row[1]
            return state


def _save_to_postgres(beta_id: str, state: Dict[str, Any], *, expected_version: Optional[int] = None) -> int:
    if expected_version is not None:
        sql = """
            UPDATE hv_beta_states
            SET state_data = %s,
                state_version = state_version + 1,
                updated_at = NOW()
            WHERE beta_id = %s
              AND state_version = %s
            RETURNING state_version
        """
        params = (json.dumps(state, ensure_ascii=False), beta_id, expected_version)
    else:
        sql = """
            INSERT INTO hv_beta_states (beta_id, state_data, state_version)
            VALUES (%s, %s, 0)
            ON CONFLICT (beta_id) DO UPDATE
            SET state_data = EXCLUDED.state_data,
                state_version = hv_beta_states.state_version + 1,
                updated_at = NOW()
            RETURNING state_version
        """
        params = (beta_id, json.dumps(state, ensure_ascii=False))

    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            if not row:
                raise StateVersionConflictError(
                    f"Version conflict for beta_id={beta_id}. "
                    f"expected={expected_version}"
                )
            return int(row[0])


def load_state(beta_id: str) -> Optional[Dict[str, Any]]:
    """
    Política de lectura (Fase 1):
    - Si HV_STATE_PERSISTENCE apunta a postgres/dual y DB disponible → leer de Postgres.
    - Si falla la lectura a Postgres → fallback a archivo (con advertencia).
    - En modo "files" puro → solo archivos.
    """
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if prefer_postgres:
        try:
            state = _load_from_postgres(beta_id)
            if state is not None:
                # Quitamos la clave interna de versión antes de devolver (el caller la maneja aparte)
                state.pop("_state_version", None)
                return state
            # No existía en DB → intentamos archivo como fuente de bootstrap
            return _load_from_file(beta_id)
        except Exception as e:
            print(f"[state-persistence] WARN: postgres load failed for {beta_id}: {e}. Falling back to file.")
            return _load_from_file(beta_id)

    # Modo files (o postgres no disponible)
    return _load_from_file(beta_id)


def save_state(
    beta_id: str,
    state: Dict[str, Any],
    *,
    expected_version: Optional[int] = None,
    also_write_file: bool = False,
) -> int:
    """
    Guarda el estado.

    - expected_version: si se pasa, hace optimistic lock. Lanza StateVersionConflictError si falla.
    - also_write_file: fuerza mirror al archivo (útil en modo dual o durante cutover).
    - Devuelve el nuevo state_version (0 en bootstrap).

    Regla de dual-write:
    - Si modo=dual o also_write_file=True → también escribe el archivo.
    - La lectura siempre prefiere Postgres cuando el modo lo indica.
    """
    mode = _persistence_mode()
    do_postgres = mode in ("postgres", "dual") and _is_postgres_available()
    do_file = (mode == "files") or also_write_file or (mode == "dual")

    new_version = 0

    if do_postgres:
        try:
            new_version = _save_to_postgres(beta_id, state, expected_version=expected_version)
        except StateVersionConflictError:
            raise
        except Exception as e:
            print(f"[state-persistence] ERROR: postgres save failed for {beta_id}: {e}")
            # En caso de fallo grave en postgres, NO caemos silenciosamente a file si el modo exige postgres.
            # Dejamos que el error suba (mejor fallar ruidoso durante migración).
            raise

    if do_file:
        _save_to_file(beta_id, state)

    return new_version


def get_current_version(beta_id: str) -> Optional[int]:
    """Helper para que los callers obtengan la versión actual antes de mutar."""
    mode = _persistence_mode()
    if mode in ("postgres", "dual") and _is_postgres_available():
        try:
            with _connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT state_version FROM hv_beta_states WHERE beta_id = %s",
                        (beta_id,),
                    )
                    row = cur.fetchone()
                    return int(row[0]) if row else None
        except Exception:
            pass
    # Fallback a archivo (no tenemos versión confiable en files, devolvemos None)
    return None


def ensure_last_active(state: Dict[str, Any]) -> Dict[str, Any]:
    """Garantiza que last_active_at esté presente (lo usa ReentryHandler en Fase 4)."""
    s = dict(state)
    if not s.get("last_active_at"):
        s["last_active_at"] = _utc_now()
    return s


# ------------------------------------------------------------------
# Listado de betas (para SignalDetector y ops) - clave para SSOT Postgres
# ------------------------------------------------------------------

def list_all_betas() -> List[Dict[str, Any]]:
    """
    Devuelve lista de estados de todas las betas conocidas.
    - Si HV_STATE_PERSISTENCE apunta a postgres y está disponible → escanea directamente la tabla hv_beta_states (SSOT).
    - Si no, cae a escanear el directorio de archivos (modo files / fallback).
    Esto permite que el SignalDetector sea nativo en DB cuando corresponde.
    """
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    betas: List[Dict[str, Any]] = []

    if prefer_postgres:
        try:
            sql = """
                SELECT beta_id, state_data, state_version
                FROM hv_beta_states
                ORDER BY updated_at DESC
            """
            with _connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    for row in cur.fetchall():
                        state = row[1] if isinstance(row[1], dict) else json.loads(row[1])
                        state["_state_version"] = row[2]
                        state["beta_id"] = row[0]  # asegurar
                        betas.append(state)
            if betas:
                return betas
        except Exception as e:
            print(f"[state-persistence] WARN: postgres list_all_betas failed, falling back to files: {e}")

    # Fallback / modo files
    try:
        base = _states_dir()
        if base.exists():
            for p in sorted(base.glob("*.json")):
                beta_id = p.stem
                try:
                    data = _load_from_file(beta_id)
                    if data:
                        data["beta_id"] = beta_id
                        betas.append(data)
                except Exception:
                    continue
    except Exception:
        pass

    return betas


# ------------------------------------------------------------------
# Agent Traces (G3) — turn_number atómico + costo por evento (hv_agent_traces)
# ------------------------------------------------------------------
# Resuelve el race del turn_number denormalizado en state_data: el SSOT del turno
# es ahora hv_agent_traces. La asignación es atómica por beta mediante
# pg_advisory_xact_lock(hashtext(beta_id)) + UNIQUE(beta_id, turn_number).
# En modo files cae a un contador por-beta (best-effort, no concurrente — dev).

def _turn_counter_file(beta_id: str) -> Path:
    d = Path(os.getenv("HV_TRACES_DIR", "data/traces"))
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{beta_id}.turn"


def _next_turn_from_files(beta_id: str) -> int:
    p = _turn_counter_file(beta_id)
    current = 0
    if p.exists():
        try:
            current = int(p.read_text(encoding="utf-8").strip() or "0")
        except Exception:
            current = 0
    nxt = current + 1
    p.write_text(str(nxt), encoding="utf-8")
    return nxt


def _traces_file() -> Path:
    d = Path(os.getenv("HV_TRACES_DIR", "data/traces"))
    d.mkdir(parents=True, exist_ok=True)
    return d / "agent_traces.jsonl"


def log_trace(
    beta_id: str,
    *,
    role: str = "proactive",
    event_type: Optional[str] = None,
    action_id: Optional[str] = None,
    idemp_key: Optional[str] = None,
    model: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
    status: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    turn_number: Optional[int] = None,
) -> int:
    """
    Inserta una traza en hv_agent_traces y devuelve su turn_number.
    Si turn_number es None se asigna atómicamente (advisory lock + MAX+1 por beta).
    En modo files: append a agent_traces.jsonl + contador por-beta. Nunca lanza
    (best-effort: una falla de traza no debe tumbar el envío/ejecución).
    """
    metadata = metadata or {}
    mode = _persistence_mode()
    use_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if use_postgres:
        try:
            with _connection() as conn:
                with conn.cursor() as cur:
                    # Serializa la asignación de turno por beta dentro de la txn.
                    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (beta_id,))
                    tn = turn_number
                    if tn is None:
                        cur.execute(
                            "SELECT COALESCE(MAX(turn_number), 0) + 1 FROM hv_agent_traces WHERE beta_id = %s",
                            (beta_id,),
                        )
                        tn = int(cur.fetchone()[0])
                    cur.execute(
                        """
                        INSERT INTO hv_agent_traces
                            (beta_id, turn_number, role, event_type, action_id, idemp_key,
                             model, tokens_in, tokens_out, cost_usd, status, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING turn_number
                        """,
                        (
                            beta_id, tn, role, event_type, action_id, idemp_key,
                            model, tokens_in, tokens_out, cost_usd, status,
                            json.dumps(metadata, ensure_ascii=False),
                        ),
                    )
                    return int(cur.fetchone()[0])
        except Exception as e:
            print(f"[state-persistence] WARN: postgres log_trace failed: {e}. Falling back to files.")

    # Files fallback
    tn = turn_number if turn_number is not None else _next_turn_from_files(beta_id)
    rec = {
        "beta_id": beta_id, "turn_number": tn, "role": role, "event_type": event_type,
        "action_id": action_id, "idemp_key": idemp_key, "model": model,
        "tokens_in": tokens_in, "tokens_out": tokens_out, "cost_usd": cost_usd,
        "status": status, "metadata": metadata, "created_at": _utc_now(),
    }
    try:
        with _traces_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[state-persistence] WARN: file log_trace failed: {e}")
    return tn


def next_turn_number(beta_id: str) -> int:
    """
    Devuelve el siguiente turn_number atómico para el beta (lo reserva).
    SSOT en hv_agent_traces (postgres) o contador por-beta (files).
    Inserta una traza marcadora event_type='turn' para reservar el número.
    """
    return log_trace(beta_id, role="system", event_type="turn")


# ------------------------------------------------------------------
# Pending Actions (C1 - Postgres + UNIQUE idemp_key) - implementación autónoma
# ------------------------------------------------------------------
# Objetivo: hacer que las acciones proactivas sean idempotentes de forma
# fuerte cuando usamos HV_STATE_PERSISTENCE=postgres.
# El UNIQUE en idemp_key (beta:signal:action:fecha) previene doble ejecución
# incluso si API y cron corren al mismo tiempo.
#
# Mantiene compatibilidad total con el path de archivos (fallback + dual).
# Sigue exactamente la misma política de lectura/escritura que load_state/save_state.

def _load_pending_from_postgres(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Carga pending actions desde Postgres (cuando está disponible)."""
    sql = """
        SELECT beta_id, action_id, idemp_key, signal_type, action_type,
               suggested_message, status, created_at, executed_at,
               dry_run, block_reason, metadata
        FROM hv_pending_actions
        WHERE 1=1
    """
    params: list = []
    if beta_id:
        sql += " AND beta_id = %s"
        params.append(beta_id)
    if status:
        sql += " AND status = %s"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    actions: List[Dict[str, Any]] = []
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            for row in cur.fetchall():
                actions.append({
                    "beta_id": row[0],
                    "action_id": row[1],
                    "idemp_key": row[2],
                    "signal": {"signal_type": row[3]},
                    "action_type": row[4],
                    "suggested_message": row[5],
                    "status": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "executed_at": row[8].isoformat() if row[8] else None,
                    "dry_run": row[9],
                    "block_reason": row[10],
                    "metadata": row[11] or {},
                })
    return actions


def _persist_pending_to_postgres(action: Dict[str, Any]) -> None:
    """Inserta (o ignora si ya existe por idemp_key)."""
    sql = """
        INSERT INTO hv_pending_actions
            (beta_id, action_id, idemp_key, signal_type, action_type,
             suggested_message, status, created_at, dry_run, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (idemp_key) DO NOTHING
    """
    params = (
        action.get("beta_id"),
        action.get("action_id"),
        action.get("idemp_key"),
        (action.get("signal") or {}).get("signal_type"),
        action.get("action_type"),
        action.get("suggested_message"),
        action.get("status", "pending"),
        action.get("created_at"),
        action.get("dry_run", False),
        action.get("metadata") or {},
    )
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def _mark_executed_in_postgres(
    action_id: str,
    idemp_key: str,
    *,
    dry_run: bool = False,
    executed_at: Optional[str] = None,
    block_reason: Optional[Dict] = None,
    final_status: Optional[str] = None,
) -> None:
    """Marca una acción como ejecutada (o bloqueada) en Postgres."""
    status = final_status or ("dry_run_executed" if dry_run else "executed")
    sql = """
        UPDATE hv_pending_actions
        SET status = %s,
            executed_at = COALESCE(%s, NOW()),
            dry_run = %s,
            block_reason = %s
        WHERE action_id = %s OR idemp_key = %s
    """
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                status,
                executed_at,
                dry_run,
                json.dumps(block_reason) if block_reason else None,
                action_id,
                idemp_key,
            ))


def _is_idemp_executed_pg(idemp_key: str) -> bool:
    """Chequeo atómico por idemp_key (usado antes de side-effects)."""
    if not idemp_key:
        return False
    sql = """
        SELECT 1 FROM hv_pending_actions
        WHERE idemp_key = %s
          AND status IN ('executed', 'dry_run_executed', 'already_executed')
        LIMIT 1
    """
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (idemp_key,))
            return cur.fetchone() is not None


# ------------------------------------------------------------------
# API pública para Pending Actions (con branching postgres / files)
# ------------------------------------------------------------------

def load_pending_actions(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Carga acciones pendientes.
    - Si HV_STATE_PERSISTENCE=postgres y DB disponible → lee de hv_pending_actions (SSOT).
    - Fallback a archivos JSONL solo en error (o modo files).
    """
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if prefer_postgres:
        try:
            actions = _load_pending_from_postgres(status=status, limit=limit, beta_id=beta_id)
            if actions:
                return actions
            # Si no hay en DB, caemos a files (posible bootstrap)
            return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)
        except Exception as e:
            print(f"[state-persistence] WARN: postgres load_pending failed: {e}. Falling back to files.")
            return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)

    return _load_pending_from_files(status=status, limit=limit, beta_id=beta_id)


def persist_pending_action(action: Dict[str, Any]) -> None:
    """
    Persiste una acción pendiente.
    En postgres: INSERT con ON CONFLICT (idemp_key) DO NOTHING → protección C1 nativa.
    En files: append (comportamiento legacy).
    """
    mode = _persistence_mode()
    do_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if do_postgres:
        try:
            _persist_pending_to_postgres(action)
            # En dual también escribimos a files para transición segura
            if mode == "dual":
                _persist_pending_to_file(action)
            return
        except Exception as e:
            print(f"[state-persistence] WARN: postgres persist_pending failed: {e}. Falling back to files.")
            # No re-raise: mejor persistir en files que perder la acción

    _persist_pending_to_file(action)


def mark_pending_executed(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    executed_at: Optional[str] = None,
    block_reason: Optional[Dict] = None,
    final_status: Optional[str] = None,
) -> None:
    """Marca como ejecutada/bloqueada. Usa PG cuando corresponde."""
    mode = _persistence_mode()
    do_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if do_postgres:
        try:
            _mark_executed_in_postgres(
                action.get("action_id", ""),
                action.get("idemp_key", ""),
                dry_run=dry_run,
                executed_at=executed_at,
                block_reason=block_reason,
                final_status=final_status,
            )
            if mode == "dual":
                _mark_executed_in_file(action, dry_run=dry_run, final_status=final_status)
            return
        except Exception as e:
            print(f"[state-persistence] WARN: postgres mark_executed failed: {e}. Using files.")

    _mark_executed_in_file(action, dry_run=dry_run, final_status=final_status)


def is_idemp_already_executed(idemp_key: str) -> bool:
    """Chequeo unificado (PG primero). Usado en execute para C1."""
    mode = _persistence_mode()
    prefer_postgres = mode in ("postgres", "dual") and _is_postgres_available()

    if prefer_postgres:
        try:
            if _is_idemp_executed_pg(idemp_key):
                return True
        except Exception as e:
            print(f"[state-persistence] WARN: postgres idemp check failed: {e}. Falling to files.")

    # Fallback / files
    return _is_idemp_executed_file(idemp_key)


# ------------------------------------------------------------------
# Helpers de archivos (para compatibilidad y fallback)
# ------------------------------------------------------------------

def _pending_dir() -> Path:
    raw = os.getenv("HV_PENDING_ACTIONS_DIR", "data/pending_actions")
    p = Path(raw)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _pending_file() -> Path:
    return _pending_dir() / "pending_actions.jsonl"


def _executed_file() -> Path:
    return _pending_dir() / "executed_actions.jsonl"


def _load_pending_from_files(
    status: Optional[str] = "pending",
    limit: int = 50,
    beta_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    path = _pending_file()
    if not path.exists():
        return []
    actions: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
                if status is None or a.get("status") == status:
                    if beta_id is None or a.get("beta_id") == beta_id:
                        actions.append(a)
            except Exception:
                continue
    return actions[-limit:][::-1] if limit else actions


def _persist_pending_to_file(action: Dict[str, Any]) -> None:
    path = _pending_file()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")


def _mark_executed_in_file(
    action: Dict[str, Any],
    *,
    dry_run: bool = False,
    final_status: Optional[str] = None,
) -> None:
    # Append a executed
    exec_path = _executed_file()
    action = dict(action)
    action["status"] = final_status or ("dry_run_executed" if dry_run else "executed")
    action["executed_at"] = _utc_now()
    with exec_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")

    # Remove from pending (best effort, ya teníamos atomic en C1 previo)
    pending_path = _pending_file()
    if pending_path.exists():
        remaining = []
        with pending_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                    if a.get("action_id") != action.get("action_id"):
                        remaining.append(a)
                except Exception:
                    remaining.append(line)
        tmp = pending_path.with_name(pending_path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for a in remaining:
                if isinstance(a, dict):
                    f.write(json.dumps(a, ensure_ascii=False) + "\n")
                else:
                    f.write(str(a) + "\n")
        os.replace(tmp, pending_path)


def _is_idemp_executed_file(idemp_key: str) -> bool:
    if not idemp_key:
        return False
    exec_path = _executed_file()
    if not exec_path.exists():
        return False
    try:
        with exec_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("idemp_key") == idemp_key:
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    return False
