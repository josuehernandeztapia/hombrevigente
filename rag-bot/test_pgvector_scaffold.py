#!/usr/bin/env python3
"""Tests pgvector scaffold (sin Neon requerido en CI)."""

import os
import unittest
from unittest import mock

from pgvector_retrieval import is_pgvector_configured, vector_literal


class TestPgvectorScaffold(unittest.TestCase):
    def test_vector_literal(self):
        lit = vector_literal([0.1, 0.2, 0.3])
        self.assertTrue(lit.startswith("["))
        self.assertIn("0.100000", lit)

    def test_not_configured_sqlite(self):
        with mock.patch.dict(
            os.environ,
            {"DATABASE_URL": "sqlite:///./x.db", "HV_DATABASE_URL": ""},
            clear=False,
        ):
            self.assertFalse(is_pgvector_configured())

    def test_configured_postgres(self):
        with mock.patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=False,
        ):
            self.assertTrue(is_pgvector_configured())

    @unittest.skipUnless(
        os.getenv("HV_PGVECTOR_INTEGRATION") == "1",
        "set HV_PGVECTOR_INTEGRATION=1 for live Neon test",
    )
    def test_live_retrieve_smoke(self):
        from pgvector_retrieval import retrieve_pgvector

        rows = retrieve_pgvector("homocisteína TMG", kb_route="longevity", top_k=3)
        self.assertIsInstance(rows, list)


if __name__ == "__main__":
    unittest.main()