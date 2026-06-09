#!/usr/bin/env python3
"""Endpoint /newsletter/approve — tokens HMAC + dispatch."""

import hashlib
import hmac
import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app


def _token(secret: str, issue_path: str, action: str, exp: int) -> str:
    sig = hmac.new(
        secret.encode(),
        f"{issue_path}|{action}|{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{exp}.{sig}"


class TestNewsletterApprove(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.secret = "test-secret-approval"
        os.environ["NEWSLETTER_APPROVAL_SECRET"] = self.secret
        self.issue = "newsletter/issues/2026-06-003.md"

    def test_invalid_token(self):
        r = self.client.get(
            "/newsletter/approve",
            params={"issue": self.issue, "action": "approve", "token": "bad.token.xxx"},
        )
        self.assertEqual(r.status_code, 403)
        self.assertIn("inválido", r.text.lower())

    def test_expired_token(self):
        exp = int(time.time()) - 60
        tok = _token(self.secret, self.issue, "approve", exp)
        r = self.client.get(
            "/newsletter/approve",
            params={"issue": self.issue, "action": "approve", "token": tok},
        )
        self.assertEqual(r.status_code, 403)

    @patch("api.main.dispatch_pulso_approval", return_value={"ok": True, "status": 204})
    def test_approve_dispatches(self, mock_dispatch):
        exp = int(time.time()) + 3600
        tok = _token(self.secret, self.issue, "approve", exp)
        r = self.client.get(
            "/newsletter/approve",
            params={"issue": self.issue, "action": "approve", "token": tok},
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("Aprobación recibida", r.text)
        mock_dispatch.assert_called_once_with(self.issue, "approve")


if __name__ == "__main__":
    unittest.main()