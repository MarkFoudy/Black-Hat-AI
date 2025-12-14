"""Tests for safety gates."""

import pytest
from unittest.mock import patch
from src.safety.gates import safety_gate, simple_gate, batch_safety_gate


class TestSafetyGate:
    """Test safety_gate function."""

    @patch.dict("os.environ", {"PROHIBITED_HOSTS": "prod,payment,core-db"})
    def test_blocks_prohibited_host(self, capsys):
        """Test that prohibited hosts are automatically blocked."""
        # Test with a prohibited keyword
        result = safety_gate("ping", {"target": "prod-server-01"})
        assert result is False

        # Verify blocking message was printed
        captured = capsys.readouterr()
        assert "Blocked unsafe target" in captured.out

    @patch.dict("os.environ", {"PROHIBITED_HOSTS": "prod,payment"})
    @patch("builtins.input", return_value="y")
    def test_approves_safe_host(self, mock_input):
        """Test that safe hosts can be approved."""
        result = safety_gate("ping", {"target": "test.example.com"})
        assert result is True

    @patch.dict("os.environ", {"PROHIBITED_HOSTS": "prod"})
    @patch("builtins.input", return_value="n")
    def test_denies_on_user_reject(self, mock_input):
        """Test that user can deny safe hosts."""
        result = safety_gate("ping", {"target": "test.example.com"})
        assert result is False


class TestSimpleGate:
    """Test simple_gate function."""

    @patch("builtins.input", return_value="y")
    def test_approves_when_confirmed(self, mock_input):
        """Test approval when user confirms."""
        result = simple_gate("scan", {"target": "example.com"})
        assert result is True

    @patch("builtins.input", return_value="n")
    def test_denies_when_rejected(self, mock_input):
        """Test denial when user rejects."""
        result = simple_gate("scan", {"target": "example.com"})
        assert result is False

    @patch("builtins.input", return_value="yes")
    def test_handles_yes_variant(self, mock_input):
        """Test that 'yes' is treated as approval."""
        result = simple_gate("scan", {"target": "example.com"})
        assert result is True


class TestBatchSafetyGate:
    """Test batch_safety_gate function."""

    def test_empty_actions_list(self):
        """Test with empty actions list."""
        result = batch_safety_gate([])
        assert result == []

    @patch("builtins.input", return_value="y")
    def test_batch_approve_all(self, mock_input):
        """Test approving all actions at once."""
        actions = [
            ("ping", {"target": "host1.com"}),
            ("scan", {"target": "host2.com"}),
        ]
        results = batch_safety_gate(actions)
        assert len(results) == 2
        assert all(results)

    @patch("builtins.input", return_value="n")
    def test_batch_deny_all(self, mock_input):
        """Test denying all actions at once."""
        actions = [
            ("ping", {"target": "host1.com"}),
            ("scan", {"target": "host2.com"}),
        ]
        results = batch_safety_gate(actions)
        assert len(results) == 2
        assert not any(results)
