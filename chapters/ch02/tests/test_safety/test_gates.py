"""Tests for safety_gate (Listing 2.8)."""

import pytest
from unittest.mock import patch
from src.safety.gates import safety_gate


class TestSafetyGate:
    """Test safety_gate with exact hostname matching."""

    def test_blocks_prohibited_host(self, capsys):
        """Exact prohibited hostnames are blocked without prompting."""
        result = safety_gate("scan", {"target": "prod.example.com"})
        assert result is False
        captured = capsys.readouterr()
        assert "BLOCKED" in captured.out

    def test_blocks_payment_host(self, capsys):
        """payment.example.com is in the prohibited set."""
        result = safety_gate("scan", {"target": "payment.example.com"})
        assert result is False

    def test_blocks_core_db_host(self, capsys):
        """core-db.example.com is in the prohibited set."""
        result = safety_gate("scan", {"target": "core-db.example.com"})
        assert result is False

    def test_non_prohibited_substring_not_blocked(self):
        """A host that merely contains 'prod' as a substring is NOT blocked."""
        # "nonproduction.internal" contains "prod" but must not be auto-blocked
        with patch("builtins.input", return_value="y"):
            result = safety_gate("scan", {"target": "nonproduction.internal"})
        assert result is True

    @patch("builtins.input", return_value="y")
    def test_approves_safe_host(self, mock_input):
        """Safe hosts reach the confirmation prompt and can be approved."""
        result = safety_gate("scan", {"target": "staging.example.com"})
        assert result is True

    @patch("builtins.input", return_value="n")
    def test_denies_on_user_reject(self, mock_input):
        """Operator can deny a safe host at the confirmation prompt."""
        result = safety_gate("scan", {"target": "staging.example.com"})
        assert result is False
