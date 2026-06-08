#!/usr/bin/env python3
"""CI: golden trajectories HV."""

import subprocess
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


class TestTrajectoryRunner(unittest.TestCase):
    def test_traj_hv_006(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--id", "TRAJ-HV-006"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TRAJ-HV-006", r.stdout)
        self.assertIn("passed", r.stdout.lower())

    def test_traj_hv_005(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--id", "TRAJ-HV-005"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TRAJ-HV-005", r.stdout)
        self.assertIn("resume-sin-perder-datos", r.stdout)

    def test_all_six_trajectories(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--all"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("6/6 passed", r.stdout)

    def test_traj_hv_002(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--id", "TRAJ-HV-002"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TRAJ-HV-002", r.stdout)
        self.assertIn("post-tally-completo", r.stdout)

    def test_traj_hv_004(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--id", "TRAJ-HV-004"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TRAJ-HV-004", r.stdout)
        self.assertIn("post-clearance-desbloqueado", r.stdout)

    def test_traj_hv_003(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py", "--id", "TRAJ-HV-003"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TRAJ-HV-003", r.stdout)
        self.assertIn("merge-labs-into-intake", r.stdout)

    def test_all_p0_trajectories(self):
        r = subprocess.run(
            [sys.executable, "trajectory_runner.py"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()