"""Tests prompt_from_issue (sin API)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from prompt_from_issue import (
    BRAND_TEMPLATE,
    visual_context,
    visual_prompts_for_issue,
    write_prompt_artifact,
)

ISSUE = Path(__file__).parent / "issues" / "2026-06-002.md"


class TestPromptFromIssue(unittest.TestCase):
    def test_visual_context_parses_accionable(self):
        ctx = visual_context(ISSUE)
        self.assertEqual(ctx["numero"], "002")
        self.assertIn("metionina", ctx["accionable_title"].lower())
        self.assertTrue(ctx["tldr"])
        self.assertGreaterEqual(len(ctx["slide_headlines"]), 1)

    def test_fallback_prompts_structure(self):
        prompts = visual_prompts_for_issue(ISSUE, use_llm=False)
        self.assertEqual(prompts["source"], "fallback")
        self.assertIn("theme", prompts)
        self.assertIn(prompts["theme"], prompts["image_prompt"])
        self.assertTrue(prompts["unsplash_query"])
        self.assertGreaterEqual(len(prompts["slide_themes"]), 1)
        self.assertEqual(prompts["image_prompt"], BRAND_TEMPLATE.format(theme=prompts["theme"]))

    def test_write_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            # use real issue path but redirect assets via monkeypatch not needed —
            # write goes to newsletter/assets/
            prompts = visual_prompts_for_issue(ISSUE, use_llm=False)
            out = write_prompt_artifact(ISSUE, prompts)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text())
            self.assertEqual(data["source"], "fallback")
            self.assertIn("unsplash_query", data)
            if out.exists():
                out.unlink()


if __name__ == "__main__":
    unittest.main()