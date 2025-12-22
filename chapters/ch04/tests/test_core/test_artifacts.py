"""
Tests for src/core/artifacts.py (Listing 4.1)
"""

import json
import os
import pytest
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.artifacts import (
    Artifact,
    ScopeArtifact,
    write_jsonl,
    read_jsonl,
    iter_jsonl,
    read_artifacts,
)


class TestArtifact:
    """Tests for the Artifact dataclass."""

    def test_artifact_defaults(self):
        """Test Artifact with default values."""
        artifact = Artifact()
        assert artifact.schema == "recon-v1"
        assert artifact.host == ""
        assert artifact.a == []
        assert artifact.cname is None
        assert artifact.headers == {}
        assert artifact.waf_hint is None
        assert artifact.tls is None
        assert artifact.notes == []
        assert artifact.ts == ""

    def test_artifact_with_values(self, sample_artifact):
        """Test Artifact with provided values."""
        assert sample_artifact.host == "example.com"
        assert sample_artifact.a == ["93.184.216.34"]
        assert sample_artifact.waf_hint is False
        assert "status:200" in sample_artifact.notes

    def test_artifact_to_dict(self, sample_artifact):
        """Test Artifact.to_dict() conversion."""
        d = sample_artifact.to_dict()
        assert isinstance(d, dict)
        assert d["host"] == "example.com"
        assert d["schema"] == "recon-v1"

    def test_artifact_from_dict(self):
        """Test Artifact.from_dict() creation."""
        data = {
            "schema": "recon-v1",
            "host": "test.com",
            "a": ["1.2.3.4"],
            "waf_hint": True,
        }
        artifact = Artifact.from_dict(data)
        assert artifact.host == "test.com"
        assert artifact.waf_hint is True

    def test_artifact_roundtrip(self, sample_artifact):
        """Test Artifact to_dict and from_dict roundtrip."""
        d = sample_artifact.to_dict()
        restored = Artifact.from_dict(d)
        assert restored.host == sample_artifact.host
        assert restored.a == sample_artifact.a


class TestScopeArtifact:
    """Tests for the ScopeArtifact dataclass."""

    def test_scope_artifact_defaults(self):
        """Test ScopeArtifact with default values."""
        artifact = ScopeArtifact()
        assert artifact.schema == "scope-v1"
        assert artifact.host == ""
        assert artifact.action == ""
        assert artifact.reason == ""

    def test_scope_artifact_blocked(self):
        """Test ScopeArtifact for blocked host."""
        artifact = ScopeArtifact(
            host="prod.example.com",
            action="blocked",
            reason="matches forbidden pattern",
        )
        assert artifact.action == "blocked"


class TestWriteJsonl:
    """Tests for write_jsonl function."""

    def test_write_artifact(self, temp_artifact_file, sample_artifact):
        """Test writing an Artifact to JSONL."""
        write_jsonl(sample_artifact, str(temp_artifact_file))

        assert temp_artifact_file.exists()
        with open(temp_artifact_file) as f:
            line = f.readline()
            data = json.loads(line)
            assert data["host"] == "example.com"

    def test_write_sets_timestamp(self, temp_artifact_file):
        """Test that write_jsonl sets timestamp if not present."""
        artifact = Artifact(host="test.com")
        write_jsonl(artifact, str(temp_artifact_file))

        with open(temp_artifact_file) as f:
            data = json.loads(f.readline())
            assert data["ts"] != ""
            # Should be ISO format
            assert "T" in data["ts"]

    def test_write_preserves_timestamp(self, temp_artifact_file):
        """Test that write_jsonl preserves existing timestamp."""
        artifact = Artifact(host="test.com", ts="2025-01-01T00:00:00Z")
        write_jsonl(artifact, str(temp_artifact_file))

        with open(temp_artifact_file) as f:
            data = json.loads(f.readline())
            assert data["ts"] == "2025-01-01T00:00:00Z"

    def test_write_appends(self, temp_artifact_file):
        """Test that write_jsonl appends to existing file."""
        artifact1 = Artifact(host="first.com")
        artifact2 = Artifact(host="second.com")

        write_jsonl(artifact1, str(temp_artifact_file))
        write_jsonl(artifact2, str(temp_artifact_file))

        with open(temp_artifact_file) as f:
            lines = f.readlines()
            assert len(lines) == 2

    def test_write_creates_directories(self, tmp_path):
        """Test that write_jsonl creates parent directories."""
        nested_file = tmp_path / "deep" / "nested" / "file.jsonl"
        artifact = Artifact(host="test.com")
        write_jsonl(artifact, str(nested_file))

        assert nested_file.exists()

    def test_write_dict(self, temp_artifact_file):
        """Test writing a plain dictionary."""
        data = {"schema": "custom-v1", "key": "value"}
        write_jsonl(data, str(temp_artifact_file))

        with open(temp_artifact_file) as f:
            line = f.readline()
            loaded = json.loads(line)
            assert loaded["key"] == "value"


class TestReadJsonl:
    """Tests for read_jsonl and iter_jsonl functions."""

    def test_read_empty_file(self, temp_artifact_file):
        """Test reading non-existent file returns empty list."""
        result = read_jsonl(str(temp_artifact_file))
        assert result == []

    def test_read_artifacts(self, temp_artifact_file, sample_artifact):
        """Test reading artifacts from file."""
        write_jsonl(sample_artifact, str(temp_artifact_file))
        write_jsonl(Artifact(host="second.com"), str(temp_artifact_file))

        result = read_jsonl(str(temp_artifact_file))
        assert len(result) == 2
        assert result[0]["host"] == "example.com"
        assert result[1]["host"] == "second.com"

    def test_iter_jsonl(self, temp_artifact_file, sample_artifact):
        """Test iterating over JSONL file."""
        write_jsonl(sample_artifact, str(temp_artifact_file))

        hosts = [r["host"] for r in iter_jsonl(str(temp_artifact_file))]
        assert hosts == ["example.com"]

    def test_read_artifacts_filters_schema(self, temp_artifact_file):
        """Test read_artifacts only returns recon-v1 schema."""
        write_jsonl(Artifact(host="recon.com"), str(temp_artifact_file))
        write_jsonl(ScopeArtifact(host="scope.com", action="blocked"), str(temp_artifact_file))

        artifacts = read_artifacts(str(temp_artifact_file))
        assert len(artifacts) == 1
        assert artifacts[0].host == "recon.com"
