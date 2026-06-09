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


def _save_to_postgres(
    beta_id: str,
    state: Dict[str, Any],
    expected_version: Optional[int] = None,
) -> int:
    """
    Guarda con optimistic locking.
    - Si expected_version is None → INSERT o UPDATE sin chequeo (bootstrap).
    - Si se provee → UPDATE ... WHERE state_version = expected RETURNING state_version
    Lanza StateVersionConflictError si no afecta filas.
    Actualiza last_active_at dentro del state_data si no viene.
    """
    state = dict(state)
    state.setdefault("last_active_at", _utc_now())

    if expected_version is None:
        # Bootstrap / primera vez para este beta
        sql = """
            INSERT INTO hv_beta_states (beta_id, state_data, state_version, updated_at)
            VALUES (%s, %s::jsonb, 0, NOW())
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
                new_version = cur.fetchone()[0]
                return int(new_version)

    # Camino con lock optimista (patrón guía)
    sql = """
        UPDATE hv_beta_states
        SET state_data = %s::jsonb,
            state_version = state_version + 1,
            updated_at = NOW()
        WHERE beta_id = %s
          AND state_version = %s
        RETURNING state_version
    """
    params = (json.dumps(state, ensure_ascii=False), beta_id, expected_version)

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


def next_turn_number(beta_id: str) -> int:
    """
    Counter atómico recomendado por la Guía (punto 2 del usuario).
    SSOT de turn_number: se consulta de hv_agent_traces con IS NOT DISTINCT FROM.
    El state denormaliza el valor para lecturas rápidas (punto 1).
    Si no hay trazas aún, empieza en 1.
    """
    sql = """
        SELECT COALESCE(MAX(turn_number), 0) + 1 AS next_turn
        FROM hv_agent_traces
        WHERE beta_id IS NOT DISTINCT FROM %s
    """
    try:
        with _connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (beta_id,))
                row = cur.fetchone()
                return int(row[0]) if row else 1
    except Exception:
        # Si la tabla aún no existe o no hay trazas, empezamos en 1
        return 1


# ------------------------------------------------------------------
# API pública (usada por beta_state.py y futuros StateManager)
# ------------------------------------------------------------------

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
