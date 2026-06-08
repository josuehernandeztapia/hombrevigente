#!/usr/bin/env python3
"""Tests decision_log + knowledge_gap_detector."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from decision_log import log_rag_decision, read_decisions, redact_for_preview, RagDecisionEntry
from knowledge_gap_detector import detect_knowledge_gaps, is_gap_row
from knowledge_promote import load_pending, remove_pending, submit_promotion
from query_preprocess import strip_command_words


class TestDecisionLog(unittest.TestCase):
    def test_redact_phone(self):
        self.assertIn("[PHONE]", redact_for_preview("llama al +5214491234567"))

    def test_append_and_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.jsonl"
            log_rag_decision(
                RagDecisionEntry(
                    query="test query",
                    query_normalized="test",
                    kb_route="longevity",
                    gate_path="escalate",
                    top_score=0.4,
                ),
                path=path,
            )
            rows = read_decisions(days=7, path=path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["gate_path"], "escalate")


class TestGapDetector(unittest.TestCase):
    def test_is_gap_escalate(self):
        self.assertTrue(is_gap_row({"gate_path": "escalate", "top_score": 0.8}, gap_threshold=0.55))

    def test_is_gap_low_score(self):
        self.assertTrue(is_gap_row({"gate_path": "auto", "top_score": 0.4, "chunks_used": 3}, gap_threshold=0.55))

    def test_is_not_gap_high_score(self):
        self.assertFalse(is_gap_row({"gate_path": "auto", "top_score": 0.75, "chunks_used": 3}, gap_threshold=0.55))

    def test_detect_clusters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "log.jsonl"
            for q in ("precio bitcoin", "precio del bitcoin hoy"):
                entry = {
                    "timestamp": "2026-06-07T12:00:00+00:00",
                    "query": q,
                    "query_normalized": strip_command_words(q),
                    "gate_path": "escalate",
                    "top_score": 0.3,
                    "chunks_used": 0,
                    "kb_route": "all",
                }
                path.write_text(
                    (path.read_text(encoding="utf-8") if path.exists() else "")
                    + json.dumps(entry) + "\n",
                    encoding="utf-8",
                )
            gaps = detect_knowledge_gaps(days=30, log_path=path, max_gaps=10)
            self.assertGreaterEqual(len(gaps), 1)
            self.assertGreaterEqual(gaps[0]["frequency"], 1)


class TestKnowledgePromote(unittest.TestCase):
    def test_submit_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pending.json"
            r1 = submit_promotion(
                question="¿Horario del spa?",
                answer="Lun-Vie 9-18h con cita previa.",
                kb_route="servicios",
                from_log_id="abc123",
                path=path,
            )
            self.assertTrue(r1["success"])
            self.assertEqual(r1["status_code"], 201)
            self.assertEqual(len(load_pending(path)), 1)

            r2 = submit_promotion(
                question="¿Horario del spa?",
                answer="Otra respuesta",
                from_log_id="abc123",
                path=path,
            )
            self.assertTrue(r2.get("idempotent"))
            self.assertEqual(r2["status_code"], 200)
            self.assertEqual(len(load_pending(path)), 1)

    def test_validation_error(self):
        r = submit_promotion(question="hi", answer="short")
        self.assertFalse(r["success"])
        self.assertEqual(r["status_code"], 400)

    def test_remove_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pending.json"
            r = submit_promotion(
                question="¿Aceptan AMEX?",
                answer="Sí, todas las tarjetas principales.",
                path=path,
            )
            pid = r["promotion"]["id"]
            ok, remaining = remove_pending(pid, path=path)
            self.assertTrue(ok)
            self.assertEqual(remaining, 0)


class TestSimulateTraffic(unittest.TestCase):
    def test_simulate_writes_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "sim.jsonl"
            r = subprocess.run(
                [
                    sys.executable,
                    "scripts/simulate_traffic.py",
                    "--count",
                    "5",
                    "--seed",
                    "1",
                    "--log-path",
                    str(log_path),
                ],
                cwd=Path(__file__).resolve().parent,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            lines = [ln for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
            self.assertGreaterEqual(len(lines), 3)


class TestGapsReportScript(unittest.TestCase):
    def test_generate_local_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "qa"
            r = subprocess.run(
                [
                    sys.executable,
                    "scripts/generate_knowledge_gaps_report.py",
                    "--days",
                    "30",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=Path(__file__).resolve().parent,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            files = list(out_dir.glob("knowledge-gaps-*.md"))
            self.assertEqual(len(files), 1)
            self.assertIn("Knowledge Gaps", files[0].read_text(encoding="utf-8"))


class TestEnvThresholds(unittest.TestCase):
    def test_cosine_from_env(self):
        with mock.patch.dict(os.environ, {"HV_COSINE_HIGH": "0.75", "HV_COSINE_MIN": "0.60"}):
            import importlib
            import kb_pipeline
            importlib.reload(kb_pipeline)
            self.assertEqual(kb_pipeline.COSINE_HIGH, 0.75)
            self.assertEqual(kb_pipeline.COSINE_MIN, 0.60)
            importlib.reload(kb_pipeline)  # restore defaults for other tests


if __name__ == "__main__":
    unittest.main()