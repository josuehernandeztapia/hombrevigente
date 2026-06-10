"""
C1 idempotency tests — proactive pending actions are persisted/executed exactly once
per logical signal (idemp_key), in file mode (no DB needed).

Postgres ledger path (hv_pending_actions + ON CONFLICT) is exercised in nightly /
manually against a real DB; here we cover the file-mode dedup + execute short-circuit.

Run: python -m pytest rag-bot/test_c1_idempotency.py -q
"""
import os
import tempfile
import unittest

# Force file mode + isolated dirs BEFORE importing action_handler paths are resolved lazily,
# but set here so each call resolves the temp dir.
from action_handler import (
    persist_pending_action,
    execute_pending_action,
    load_pending_actions,
    is_idemp_already_executed,
    generate_action_for_signal,
)
from signal_detector import BetaSignal


def _action(idemp_suffix: str = "h0", status: str = "pending"):
    return {
        "beta_id": "bX",
        "action_id": f"act-bX-no_activity_7d-{idemp_suffix}",
        "idemp_key": f"bX:no_activity_7d:followup:{idemp_suffix}",
        "signal": {"signal_type": "no_activity_7d"},
        "signal_type": "no_activity_7d",
        "action_type": "reengage",
        "phase": "followup",
        "suggested_message": "Hola, retomemos.",
        "status": status,
    }


class TestC1Idempotency(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HV_STATE_PERSISTENCE"] = "files"  # no Postgres ledger
        os.environ["HV_PENDING_ACTIONS_DIR"] = self._tmp.name
        os.environ["HV_TRACES_DIR"] = self._tmp.name
        os.environ["HV_DECISION_LOG_ENABLED"] = "false"

    def tearDown(self):
        self._tmp.cleanup()

    def test_persist_dedups_by_idemp_key(self):
        a = _action("h1")
        persist_pending_action(dict(a))
        persist_pending_action(dict(a))  # duplicate logical signal
        pending = load_pending_actions(limit=100)
        same = [p for p in pending if p.get("idemp_key") == a["idemp_key"]]
        self.assertEqual(len(same), 1, "same idemp_key must persist only once")

    def test_execute_twice_is_idempotent(self):
        a = _action("h2")
        persist_pending_action(dict(a))
        pend = [p for p in load_pending_actions(limit=100) if p["idemp_key"] == a["idemp_key"]][0]

        r1 = execute_pending_action(dict(pend), dry_run=True)
        self.assertEqual(r1.get("status"), "dry_run_executed")
        self.assertTrue(is_idemp_already_executed(a["idemp_key"]))

        # A second execution of the same logical action short-circuits, no side effects.
        r2 = execute_pending_action(dict(pend), dry_run=True)
        self.assertEqual(r2.get("status"), "already_executed")

    def test_repersist_after_execute_does_not_requeue(self):
        a = _action("h3")
        persist_pending_action(dict(a))
        pend = [p for p in load_pending_actions(limit=100) if p["idemp_key"] == a["idemp_key"]][0]
        execute_pending_action(dict(pend), dry_run=True)
        # run_detect_and_act re-generating the same signal must NOT re-queue it
        persist_pending_action(_action("h3"))
        pending_same = [p for p in load_pending_actions(limit=100) if p.get("idemp_key") == a["idemp_key"]]
        self.assertEqual(len(pending_same), 0, "already-executed idemp_key must not be re-queued")

    def test_generate_action_has_stable_idemp_key(self):
        sig = BetaSignal("bY", "no_activity_72h", "medium", {"phase": "followup"})
        try:
            a1 = generate_action_for_signal(sig)
            a2 = generate_action_for_signal(sig)
        except Exception as e:  # pragma: no cover - state_manager unavailable in some envs
            self.skipTest(f"generate_action_for_signal needs state_manager: {e}")
        self.assertIn("idemp_key", a1)
        self.assertTrue(a1["idemp_key"].startswith("bY:no_activity_72h:"))
        self.assertEqual(a1["idemp_key"], a2["idemp_key"], "idemp_key must be stable for same signal+hour")


if __name__ == "__main__":
    unittest.main()
