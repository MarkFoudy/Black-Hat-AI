"""Tests for PingTool."""

import pytest
from src.tools.ping import PingTool, ping_host


class TestPingTool:
    """Test PingTool class."""

    def test_ping_tool_attributes(self):
        """Test PingTool has correct attributes."""
        tool = PingTool()
        assert tool.name == "ping"
        assert tool.description == "Checks if a host is reachable."

    def test_ping_localhost(self):
        """Test pinging localhost (should always succeed)."""
        tool = PingTool()
        result = tool.invoke({"host": "127.0.0.1"})
        assert "reachable" in result
        assert result["reachable"] is True

    def test_ping_invalid_host(self):
        """Test pinging an invalid hostname."""
        tool = PingTool()
        result = tool.invoke({"host": "this-host-definitely-does-not-exist.invalid"})
        assert "reachable" in result
        assert result["reachable"] is False

    def test_ping_host_function(self):
        """Test convenience ping_host function."""
        result = ping_host("127.0.0.1")
        assert isinstance(result, dict)
        assert "reachable" in result


class TestPingHostFunction:
    """Test ping_host convenience function."""

    def test_functional_interface(self):
        """Test the functional interface."""
        result = ping_host("127.0.0.1")
        assert result["reachable"] is True

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = ping_host("127.0.0.1")
        assert isinstance(result, dict)
