"""
Tests for src/safety/gates.py (Section 4.2.4)
"""

import os
import sys
from unittest.mock import patch
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.safety.gates import (
    time_window_gate,
    approval_gate,
    scope_gate,
    rate_limit_gate,
    environment_gate,
    GateChain,
    create_standard_gates,
)
from src.safety.scope import ScopeConfig, ScopeChecker


class TestTimeWindowGate:
    """Tests for the time_window_gate function."""

    def test_within_window(self):
        """Test gate passes when within time window."""
        with patch('src.safety.gates.datetime') as mock_dt:
            mock_now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now

            allowed, reason = time_window_gate(9, 17)

            assert allowed is True
            assert "within" in reason

    def test_outside_window_before(self):
        """Test gate fails when before time window."""
        with patch('src.safety.gates.datetime') as mock_dt:
            mock_now = datetime(2025, 1, 15, 7, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now

            allowed, reason = time_window_gate(9, 17)

            assert allowed is False
            assert "outside" in reason

    def test_outside_window_after(self):
        """Test gate fails when after time window."""
        with patch('src.safety.gates.datetime') as mock_dt:
            mock_now = datetime(2025, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now

            allowed, reason = time_window_gate(9, 17)

            assert allowed is False
            assert "outside" in reason

    def test_custom_window(self):
        """Test gate with custom time window."""
        with patch('src.safety.gates.datetime') as mock_dt:
            mock_now = datetime(2025, 1, 15, 3, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now

            # 0-24 window should always pass
            allowed, _ = time_window_gate(0, 24)
            assert allowed is True


class TestApprovalGate:
    """Tests for the approval_gate function."""

    def test_auto_approve(self):
        """Test auto-approval bypasses prompt."""
        result = approval_gate("scan", "example.com", auto_approve=True)
        assert result is True

    def test_non_interactive_denies(self):
        """Test non-interactive mode denies."""
        with patch('sys.stdin.isatty', return_value=False):
            result = approval_gate("scan", "example.com")
            assert result is False

    def test_user_approves(self):
        """Test user approval via input."""
        with patch('sys.stdin.isatty', return_value=True):
            with patch('builtins.input', return_value="y"):
                result = approval_gate("scan", "example.com")
                assert result is True

    def test_user_denies(self):
        """Test user denial via input."""
        with patch('sys.stdin.isatty', return_value=True):
            with patch('builtins.input', return_value="n"):
                result = approval_gate("scan", "example.com")
                assert result is False


class TestScopeGate:
    """Tests for the scope_gate function."""

    def test_scope_gate_allowed(self, sample_scope_checker):
        """Test scope gate allows in-scope hosts."""
        allowed, reason = scope_gate("example.com", sample_scope_checker)
        assert allowed is True

    def test_scope_gate_blocked(self, sample_scope_checker):
        """Test scope gate blocks out-of-scope hosts."""
        allowed, reason = scope_gate("other.com", sample_scope_checker)
        assert allowed is False


class TestRateLimitGate:
    """Tests for the rate_limit_gate function."""

    def test_under_limit(self):
        """Test gate passes when under limit."""
        allowed, reason = rate_limit_gate(5, 10)
        assert allowed is True
        assert "5 actions remaining" in reason

    def test_at_limit(self):
        """Test gate fails when at limit."""
        allowed, reason = rate_limit_gate(10, 10)
        assert allowed is False
        assert "exceeded" in reason

    def test_over_limit(self):
        """Test gate fails when over limit."""
        allowed, reason = rate_limit_gate(15, 10)
        assert allowed is False


class TestEnvironmentGate:
    """Tests for the environment_gate function."""

    def test_env_var_exists(self):
        """Test gate passes when env var exists."""
        with patch.dict(os.environ, {"TEST_VAR": "value"}):
            allowed, reason = environment_gate("TEST_VAR")
            assert allowed is True
            assert "configured" in reason

    def test_env_var_missing(self):
        """Test gate fails when env var missing."""
        with patch.dict(os.environ, {}, clear=True):
            allowed, reason = environment_gate("NONEXISTENT_VAR")
            assert allowed is False
            assert "missing" in reason

    def test_env_var_value_match(self):
        """Test gate passes when value matches."""
        with patch.dict(os.environ, {"TEST_VAR": "expected"}):
            allowed, _ = environment_gate("TEST_VAR", expected_value="expected")
            assert allowed is True

    def test_env_var_value_mismatch(self):
        """Test gate fails when value doesn't match."""
        with patch.dict(os.environ, {"TEST_VAR": "actual"}):
            allowed, reason = environment_gate("TEST_VAR", expected_value="expected")
            assert allowed is False
            assert "unexpected value" in reason


class TestGateChain:
    """Tests for the GateChain class."""

    def test_empty_chain_passes(self):
        """Test empty chain passes."""
        chain = GateChain()
        passed, reasons = chain.check()
        assert passed is True
        assert reasons == []

    def test_all_gates_pass(self):
        """Test chain passes when all gates pass."""
        chain = GateChain()
        chain.add(lambda: (True, "gate 1 passed"))
        chain.add(lambda: (True, "gate 2 passed"))

        passed, reasons = chain.check()

        assert passed is True
        assert len(reasons) == 2

    def test_one_gate_fails(self):
        """Test chain fails when any gate fails."""
        chain = GateChain()
        chain.add(lambda: (True, "gate 1 passed"))
        chain.add(lambda: (False, "gate 2 failed"))

        passed, reasons = chain.check()

        assert passed is False
        assert len(reasons) == 2

    def test_chain_method_chaining(self):
        """Test fluent chain building."""
        chain = (
            GateChain()
            .add(lambda: (True, "a"))
            .add(lambda: (True, "b"))
        )

        assert len(chain.gates) == 2


class TestCreateStandardGates:
    """Tests for the create_standard_gates factory function."""

    def test_create_with_time_gate(self):
        """Test creating chain with time gate."""
        chain = create_standard_gates(enable_time_gate=True)
        assert len(chain.gates) == 1

    def test_create_with_scope(self, sample_scope_checker):
        """Test creating chain with scope checker."""
        chain = create_standard_gates(
            scope_checker=sample_scope_checker,
            host="example.com",
        )
        assert len(chain.gates) == 1

    def test_create_with_both(self, sample_scope_checker):
        """Test creating chain with both gates."""
        chain = create_standard_gates(
            scope_checker=sample_scope_checker,
            host="example.com",
            enable_time_gate=True,
        )
        assert len(chain.gates) == 2
