"""Tests del dual-write Postgres de decision_log (migración 004).

Sin DB real: se monkeypatchea decision_log._connection con un fake que captura
los execute(). Verifica el contrato fail-open y la política de lectura
(Postgres primero, archivo como fallback; path explícito = archivo puro).
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pytest

import decision_log
from decision_log import RagDecisionEntry, log_rag_decision, read_decisions


@pytest.fixture(autouse=True)
def _logging_on(monkeypatch):
    # Otras suites del run combinado apagan el log vía os.environ sin cleanup
    # (test_whatsapp_channel, test_c1_idempotency, …). Re-encender siempre aquí.
    monkeypatch.setenv("HV_DECISION_LOG_ENABLED", "true")
    monkeypatch.delenv("HV_DECISION_LOG_PG", raising=False)


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.conn.executed.append((sql.strip(), params))

    def fetchall(self):
        return self.conn.rows


class FakeConn:
    def __init__(self, rows=None):
        self.executed = []
        self.rows = rows or []

    def cursor(self):
        return FakeCursor(self)


def _fake_connection_factory(conn):
    @contextmanager
    def _cm():
        yield conn

    return _cm


def _entry(**kw) -> RagDecisionEntry:
    defaults = dict(
        query="¿precio de morpheus8?",
        query_normalized="precio morpheus8",
        kb_route="servicios",
        gate_path="rag",
    )
    defaults.update(kw)
    return RagDecisionEntry(**defaults)


def _enable_pg(monkeypatch, conn):
    monkeypatch.setattr(decision_log, "_connection", _fake_connection_factory(conn))
    monkeypatch.setattr(decision_log, "is_pgvector_configured", lambda: True)


def test_dual_write_inserts_to_postgres(tmp_path, monkeypatch):
    monkeypatch.setenv("HV_DECISION_LOG_PATH", str(tmp_path / "log.jsonl"))
    conn = FakeConn()
    _enable_pg(monkeypatch, conn)

    entry_id = log_rag_decision(_entry(beta_id="beta-x"))

    assert entry_id
    assert len(conn.executed) == 1
    sql, params = conn.executed[0]
    assert "hv_decision_log" in sql and "ON CONFLICT" in sql
    assert params[0] == entry_id
    assert params[2] == "beta-x"
    payload = json.loads(params[-1])
    assert payload["kb_route"] == "servicios"
    # El archivo también se escribió (dual-write)
    assert (tmp_path / "log.jsonl").exists()


def test_pg_failure_is_fail_open(tmp_path, monkeypatch):
    monkeypatch.setenv("HV_DECISION_LOG_PATH", str(tmp_path / "log.jsonl"))

    @contextmanager
    def _boom():
        raise RuntimeError("db caída")
        yield  # pragma: no cover

    monkeypatch.setattr(decision_log, "_connection", _boom)
    monkeypatch.setattr(decision_log, "is_pgvector_configured", lambda: True)

    entry_id = log_rag_decision(_entry())

    # La caída de Postgres no rompe ni pierde el registro local
    assert entry_id
    assert (tmp_path / "log.jsonl").read_text(encoding="utf-8").strip()


def test_read_prefers_postgres(tmp_path, monkeypatch):
    monkeypatch.setenv("HV_DECISION_LOG_PATH", str(tmp_path / "empty.jsonl"))
    row = {
        "entry_id": "abc123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": "[redacted]",
        "kb_route": "longevity",
    }
    conn = FakeConn(rows=[(row,)])
    _enable_pg(monkeypatch, conn)

    rows = read_decisions(days=7)

    assert rows == [row]
    sql, params = conn.executed[0]
    assert "FROM hv_decision_log" in sql


def test_read_falls_back_to_file_when_pg_empty(tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"
    monkeypatch.setenv("HV_DECISION_LOG_PATH", str(log))
    conn = FakeConn(rows=[])
    _enable_pg(monkeypatch, conn)
    log_rag_decision(_entry(), path=log)  # solo archivo

    rows = read_decisions(days=7)

    assert len(rows) == 1
    assert rows[0]["kb_route"] == "servicios"


def test_explicit_path_skips_postgres(tmp_path, monkeypatch):
    conn = FakeConn()
    _enable_pg(monkeypatch, conn)
    log = tmp_path / "log.jsonl"

    log_rag_decision(_entry(), path=log)
    rows = read_decisions(days=7, path=log)

    assert conn.executed == []  # ni write ni read tocaron la DB
    assert len(rows) == 1


def test_env_kill_switch(tmp_path, monkeypatch):
    monkeypatch.setenv("HV_DECISION_LOG_PATH", str(tmp_path / "log.jsonl"))
    monkeypatch.setenv("HV_DECISION_LOG_PG", "false")
    conn = FakeConn()
    _enable_pg(monkeypatch, conn)

    log_rag_decision(_entry())

    assert conn.executed == []


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
