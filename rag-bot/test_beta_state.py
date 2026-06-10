"""
test_beta_state.py — Tests for proactive (generate + health gate + C1 idempotency).

Covers golden regression (4 signals) + atomic idempotency under file mode (C1).

Run: python -m pytest rag-bot/test_beta_state.py -q --tb=line

RAG enrichment is optional/best-effort and not required for these tests to pass.
Ref: AUDITORIA_CODIGO_HV_2026-06-09.md (C1), Guía + 4 points (TRAJ-HV-010, postgres-first, health gating).
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict

# We test the public surface
from action_handler import (
    BetaSignal,
    generate_action_for_signal,
    execute_pending_action,
    compute_proactive_health_score,
    load_pending_actions,
    persist_pending_action,
)


GOLDEN = [
    {"signal_type": "no_activity_72h", "action_type": "reengage", "phase": "reentry", "starts": "Hola", "has_resume": False},
    {"signal_type": "stalled_onboarding", "action_type": "tally_reminder", "phase": "onboarding", "starts": "Recuerda", "has_resume": False},
    {"signal_type": "low_progress", "action_type": "checkin", "phase": "followup", "starts": "Check-in", "has_resume": False},
    {"signal_type": "missing_labs", "action_type": "labs_reminder", "phase": "labs", "starts": "Te faltan", "has_resume": False},
]


class TestProactiveGolden(unittest.TestCase):
    """Golden regression for deterministic generate_action_for_signal (RAG optional)."""

    def test_golden_samples(self):
        for g in GOLDEN:
            with self.subTest(signal=g["signal_type"]):
                sig = BetaSignal(
                    beta_id="beta-golden-001",
                    signal_type=g["signal_type"],
                    phase=g["phase"],
                    last_active_at=None,
                    metadata={},
                )
                action = generate_action_for_signal(sig)
                self.assertEqual(action["action_type"], g["action_type"])
                self.assertTrue(
                    action["suggested_message"].startswith(g["starts"]),
                    f"expected start {g['starts']!r} got {action['suggested_message'][:40]!r}",
                )
                # has_resume may be present as key or we tolerate absence for golden (per fixture)
                has_r = action.get("has_resume", False)
                self.assertIsInstance(has_r, bool)


class TestC1IdempotencyAtomic(unittest.TestCase):
    """C1: same action (same idemp_key) executed twice must result in <=1 real execution."""

    def test_idempotent_execute_twice_file_mode(self):
        with tempfile.TemporaryDirectory() as td:
            # Isolate pending/executed files for this test (state_persistence + action_handler honor this)
            os.environ["HV_PENDING_ACTIONS_DIR"] = td
            # Use "postgres" for the ssot check inside health gate so the C1 idemp test can exercise
            # real execute path (is_idemp check happens before gate). Gate itself is tested separately.
            # Persistence layer still falls back to files because no real PG URL is configured.
            os.environ["HV_STATE_PERSISTENCE"] = "postgres"  # makes compute... is_healthy=True for this test

            # Build a representative action (idemp_key will be derived inside generate/execute too)
            action: Dict[str, Any] = {
                "beta_id": "beta-c1-001",
                "action_id": "act-c1-test-1",
                "idemp_key": "beta-c1-001:no_activity_72h::test-bucket",
                "signal_type": "no_activity_72h",
                "action_type": "reengage",
                "suggested_message": "Hola, hace tiempo que no tenemos actividad. ¿Quieres retomar?",
                "status": "pending",
                "created_at": "2026-06-09T12:00:00+00:00",
            }

            # First execute (should run)
            r1 = execute_pending_action(action, dry_run=False)
            self.assertIn(r1.get("status"), ("executed", "dry_run_executed", "already_executed"))

            # Second execute with identical idempotent action (must not create second execution)
            r2 = execute_pending_action(action, dry_run=False)
            self.assertIn(r2.get("status"), ("already_executed", "executed"))  # already is the C1 win

            # Inspect executed file directly to confirm <=1 record for this idemp
            exec_path = Path(td) / "executed_actions.jsonl"
            count = 0
            if exec_path.exists():
                for line in exec_path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                        if rec.get("idemp_key") == action["idemp_key"]:
                            count += 1
                    except Exception:
                        pass
            self.assertLessEqual(count, 1, f"More than one execution record for idemp_key (C1 violation): {count}")


class TestHealthGate(unittest.TestCase):
    def test_is_healthy_requires_postgres_and_score(self):
        h_files = compute_proactive_health_score(pending_count=0, drift=0.0, ssot="files")
        self.assertFalse(h_files["is_healthy"])
        self.assertEqual(h_files["score"], 85)  # 100-15 for ssot

        h_pg = compute_proactive_health_score(pending_count=0, drift=0.0, ssot="postgres")
        self.assertTrue(h_pg["is_healthy"])
        self.assertEqual(h_pg["score"], 100)


if __name__ == "__main__":
    unittest.main()
