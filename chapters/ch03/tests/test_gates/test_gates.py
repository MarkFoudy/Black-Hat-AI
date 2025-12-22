"""
Tests for safety gates.

From Listings 3.5 and 3.6 in Black Hat AI.
"""

import pytest
from datetime import time

from src.gates import (
    GlobalGate,
    ScopeGate,
    TimeWindowGate,
    ApprovalGate,
    EnvironmentGate,
)


class MockStage:
    """Mock stage for testing gates."""

    def __init__(self, name: str, target: str = None, targets: list = None):
        self.name = name
        self.target = target
        self.targets = targets or ([target] if target else [])


class TestGlobalGate:
    """Tests for GlobalGate (Listing 3.6)."""

    def test_allows_within_window(self):
        """Test that gate allows within time window."""
        # 0-23 allows all hours
        gate = GlobalGate(start_hour=0, end_hour=23)
        stage = MockStage("test")

        assert gate.allow(stage) is True

    def test_disabled_gate_allows_all(self):
        """Test that disabled gate always allows."""
        gate = GlobalGate(start_hour=0, end_hour=1, enabled=False)
        stage = MockStage("test")

        assert gate.allow(stage) is True


class TestScopeGate:
    """Tests for ScopeGate."""

    def test_allows_authorized_domain(self):
        """Test allowing authorized domains."""
        gate = ScopeGate(authorized_domains=["example.com"])
        stage = MockStage("scan", target="api.example.com")

        assert gate.allow(stage) is True

    def test_blocks_unauthorized_domain(self):
        """Test blocking unauthorized domains."""
        gate = ScopeGate(authorized_domains=["example.com"])
        stage = MockStage("scan", target="api.other.com")

        assert gate.allow(stage) is False

    def test_blocks_excluded_pattern(self):
        """Test blocking excluded patterns."""
        gate = ScopeGate(
            authorized_domains=["example.com"],
            excluded_patterns=["prod"],
        )
        stage = MockStage("scan", target="prod.example.com")

        assert gate.allow(stage) is False

    def test_allows_without_targets(self):
        """Test that stages without targets are allowed."""
        gate = ScopeGate(authorized_domains=["example.com"])
        stage = MockStage("process")

        assert gate.allow(stage) is True


class TestTimeWindowGate:
    """Tests for TimeWindowGate."""

    def test_default_weekdays(self):
        """Test default configuration (Mon-Fri)."""
        gate = TimeWindowGate()

        # Default is Mon-Fri (0-4)
        assert gate.allowed_days == [0, 1, 2, 3, 4]


class TestApprovalGate:
    """Tests for ApprovalGate."""

    def test_auto_approve(self):
        """Test auto-approval mode."""
        gate = ApprovalGate(auto_approve=True)
        stage = MockStage("exploit")

        assert gate.allow(stage) is True

    def test_selective_approval(self):
        """Test that only specified stages require approval."""
        gate = ApprovalGate(
            require_approval_for=["exploit", "exfil"],
            auto_approve=True,
        )

        # Recon doesn't need approval
        assert gate.allow(MockStage("recon")) is True
        # Exploit needs approval (auto-approved here)
        assert gate.allow(MockStage("exploit")) is True


class TestEnvironmentGate:
    """Tests for EnvironmentGate (Listing 3.5)."""

    def test_blocks_prod_target(self):
        """Test blocking production targets."""
        gate = EnvironmentGate(
            prohibited_patterns=["prod"],
            check_hostname=False,
        )
        stage = MockStage("scan", target="prod.example.com")

        assert gate.allow(stage) is False

    def test_allows_safe_target(self):
        """Test allowing non-production targets."""
        gate = EnvironmentGate(
            prohibited_patterns=["prod", "payment"],
            check_hostname=False,
        )
        stage = MockStage("scan", target="staging.example.com")

        assert gate.allow(stage) is True

    def test_multiple_prohibited_patterns(self):
        """Test multiple prohibited patterns."""
        gate = EnvironmentGate(
            prohibited_patterns=["prod", "payment", "core-db"],
            check_hostname=False,
        )

        assert gate.allow(MockStage("scan", target="payment.example.com")) is False
        assert gate.allow(MockStage("scan", target="core-db.example.com")) is False
        assert gate.allow(MockStage("scan", target="api.example.com")) is True

    def test_case_insensitive(self):
        """Test that pattern matching is case-insensitive."""
        gate = EnvironmentGate(
            prohibited_patterns=["prod"],
            check_hostname=False,
        )

        assert gate.allow(MockStage("scan", target="PROD.example.com")) is False
        assert gate.allow(MockStage("scan", target="Prod.Example.COM")) is False
