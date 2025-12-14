"""Tests for core data models (Message and Observation)."""

import pytest
from datetime import datetime
from src.core.models import Message, Observation


class TestMessage:
    """Test Message model."""

    def test_message_creation(self):
        """Test creating a basic message."""
        msg = Message(role="user", content="Hello, agent!")
        assert msg.role == "user"
        assert msg.content == "Hello, agent!"
        assert isinstance(msg.timestamp, datetime)
        assert msg.meta is None

    def test_message_with_metadata(self):
        """Test message with metadata."""
        meta = {"priority": "high", "source": "api"}
        msg = Message(role="system", content="Warning!", meta=meta)
        assert msg.meta == meta
        assert msg.meta["priority"] == "high"

    def test_message_roles(self):
        """Test different message roles."""
        roles = ["system", "user", "agent", "tool"]
        for role in roles:
            msg = Message(role=role, content=f"Test {role}")
            assert msg.role == role


class TestObservation:
    """Test Observation model."""

    def test_observation_success(self):
        """Test successful observation."""
        obs = Observation(
            tool_name="ping",
            input={"host": "example.com"},
            output={"reachable": True},
            success=True,
        )
        assert obs.tool_name == "ping"
        assert obs.success is True
        assert obs.error is None
        assert isinstance(obs.timestamp, datetime)

    def test_observation_failure(self):
        """Test failed observation with error."""
        obs = Observation(
            tool_name="scan",
            input={"target": "blocked.example.com"},
            output={},
            success=False,
            error="Connection refused",
        )
        assert obs.success is False
        assert obs.error == "Connection refused"

    def test_observation_with_complex_data(self):
        """Test observation with nested data structures."""
        obs = Observation(
            tool_name="port_scan",
            input={"host": "example.com", "ports": [80, 443, 8080]},
            output={
                "80": {"status": "open", "service": "http"},
                "443": {"status": "open", "service": "https"},
                "8080": {"status": "closed"},
            },
            success=True,
        )
        assert len(obs.output) == 3
        assert obs.output["443"]["service"] == "https"
