"""Tests llm_client (sin red)."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from llm_client import (
    DEFAULT_ANTHROPIC_COMPOSE,
    DEFAULT_OPENAI_COMPOSE,
    resolve_compose_llm,
)


class TestLLMClient(unittest.TestCase):
    def test_auto_prefers_anthropic(self):
        env = {
            "PULSO_COMPOSE_PROVIDER": "auto",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "OPENAI_API_KEY": "sk-openai-test",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = resolve_compose_llm()
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.provider, "anthropic")
        self.assertEqual(cfg.model, DEFAULT_ANTHROPIC_COMPOSE)

    def test_auto_openai_only(self):
        env = {
            "PULSO_COMPOSE_PROVIDER": "auto",
            "OPENAI_API_KEY": "sk-openai-test",
        }
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            cfg = resolve_compose_llm()
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.provider, "openai")
        self.assertEqual(cfg.model, DEFAULT_OPENAI_COMPOSE)

    def test_model_override(self):
        env = {
            "PULSO_COMPOSE_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "PULSO_COMPOSE_MODEL": "gpt-4o-mini",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = resolve_compose_llm()
        self.assertEqual(cfg.model, "gpt-4o-mini")

    def test_no_keys(self):
        with patch.dict(os.environ, {"PULSO_COMPOSE_PROVIDER": "auto"}, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            self.assertIsNone(resolve_compose_llm())


if __name__ == "__main__":
    unittest.main()