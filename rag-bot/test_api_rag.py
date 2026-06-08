#!/usr/bin/env python3
"""API RAG — beta_id + health (sin servidor externo)."""

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

_ROOT = Path(__file__).resolve().parent


class TestApiRag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        idx = _ROOT / "knowledge_base" / "embeddings_local.json"
        if not idx.exists():
            raise unittest.SkipTest("embeddings_local.json missing — run embed_kb_local.py")
        os.environ["HV_EMBEDDINGS_INDEX"] = str(idx)
        os.environ["OPENAI_API_KEY"] = ""
        from api.main import app

        cls.client = TestClient(app)

    def test_health_beta_fixture(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body.get("beta_fixture_row_0"))
        self.assertIn(body.get("status"), ("ok", "degraded"))

    def test_post_rag_beta_id_frozen_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HV_BETA_STATES_DIR"] = tmp
            r = self.client.post(
                "/rag/query?parse=1&use_llm=false",
                json={
                    "query": "¿puedo hacer ayuno 16:8?",
                    "beta_id": "row-0",
                    "use_llm": False,
                    "channel": "api",
                },
            )
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            self.assertEqual(body.get("beta_id"), "row-0")
            self.assertEqual(body.get("gate_path"), "blocked")
            self.assertEqual(body.get("gate"), "gate_psiquiatria")
            self.assertIn("frozen_context", body)
            self.assertIn("litio", body["frozen_context"].lower())

    def test_get_rag_beta_id_param(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["HV_BETA_STATES_DIR"] = tmp
            r = self.client.get(
                "/rag/query",
                params={
                    "q": "¿puedo hacer ayuno 16:8?",
                    "beta_id": "row-0",
                    "use_llm": "false",
                    "parse": "1",
                },
            )
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            self.assertEqual(body.get("beta_id"), "row-0")
            self.assertEqual(body.get("gate_path"), "blocked")


if __name__ == "__main__":
    unittest.main()