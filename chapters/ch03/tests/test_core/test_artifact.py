"""
Tests for PipelineArtifact.

From Listing 3.2 in Black Hat AI.
"""

import pytest
from datetime import datetime

from src.core.artifact import PipelineArtifact


class TestPipelineArtifact:
    """Tests for PipelineArtifact class."""

    def test_create_artifact(self):
        """Test basic artifact creation."""
        artifact = PipelineArtifact(
            stage="test",
            input={"key": "value"},
            output={"result": "success"},
            success=True,
        )

        assert artifact.stage == "test"
        assert artifact.input == {"key": "value"}
        assert artifact.output == {"result": "success"}
        assert artifact.success is True
        assert artifact.run_id is not None
        assert artifact.timestamp is not None

    def test_artifact_auto_run_id(self):
        """Test that run_id is auto-generated."""
        artifact1 = PipelineArtifact(
            stage="test",
            input={},
            output={},
            success=True,
        )
        artifact2 = PipelineArtifact(
            stage="test",
            input={},
            output={},
            success=True,
        )

        assert artifact1.run_id != artifact2.run_id

    def test_to_jsonl_record(self):
        """Test JSONL serialization."""
        artifact = PipelineArtifact(
            stage="triage",
            input={"targets": ["example.com"]},
            output={"high_risk": ["admin.example.com"]},
            success=True,
        )

        record = artifact.to_jsonl_record()

        assert record["stage"] == "triage"
        assert isinstance(record["timestamp"], str)
        assert "T" in record["timestamp"]  # ISO format

    def test_from_previous(self):
        """Test artifact chaining with from_previous."""
        first = PipelineArtifact(
            stage="recon",
            input={},
            output={"hosts": ["host1", "host2"]},
            success=True,
        )

        second = PipelineArtifact.from_previous(
            previous=first,
            stage="triage",
            output={"high_risk": ["host1"]},
            success=True,
        )

        # Should inherit run_id
        assert second.run_id == first.run_id
        # Input should be previous output
        assert second.input == {"hosts": ["host1", "host2"]}

    def test_from_previous_none(self):
        """Test from_previous with no previous artifact."""
        artifact = PipelineArtifact.from_previous(
            previous=None,
            stage="recon",
            output={"data": "result"},
            success=True,
        )

        assert artifact.run_id is not None
        assert artifact.input == {}

    def test_failed_artifact(self):
        """Test artifact with error."""
        artifact = PipelineArtifact(
            stage="triage",
            input={"data": "test"},
            output={},
            success=False,
            error="Connection timeout",
        )

        assert artifact.success is False
        assert artifact.error == "Connection timeout"
