"""
Tests for ReconNormalizeAgent.
"""

import pytest
from src.agents.recon_normalize import ReconNormalizeAgent, infer_signals
from src.core.artifact import PipelineArtifact


class TestInferSignals:
    """Test signal inference logic."""

    def test_admin_panel_signal(self):
        """Should detect admin panel from hostname."""
        record = {"host": "admin.example.com"}
        signals = infer_signals(record)
        assert "admin_panel" in signals

    def test_non_production_signal(self):
        """Should detect staging/dev environments."""
        record = {"host": "staging.example.com"}
        signals = infer_signals(record)
        assert "non_production" in signals

        record = {"host": "dev.example.com"}
        signals = infer_signals(record)
        assert "non_production" in signals

    def test_debug_enabled_signal(self):
        """Should detect debug headers."""
        record = {
            "host": "api.example.com",
            "headers": {"x-debug-mode": "enabled"},
        }
        signals = infer_signals(record)
        assert "debug_enabled" in signals

    def test_tech_disclosure_signal(self):
        """Should detect technology disclosure headers."""
        record = {
            "host": "api.example.com",
            "headers": {"x-powered-by": "PHP/7.4"},
        }
        signals = infer_signals(record)
        assert "tech_disclosure" in signals

    def test_sensitive_port_signal(self):
        """Should detect sensitive ports."""
        record = {"host": "db.example.com", "ports": [22, 5432]}
        signals = infer_signals(record)
        assert "sensitive_port" in signals

    def test_dev_port_signal(self):
        """Should detect development ports."""
        record = {"host": "api.example.com", "ports": [3000, 8080]}
        signals = infer_signals(record)
        assert "dev_port" in signals

    def test_multiple_signals(self):
        """Should detect multiple signals from same record."""
        record = {
            "host": "admin.staging.example.com",
            "headers": {"x-debug-mode": "enabled"},
            "ports": [22, 3000],
        }
        signals = infer_signals(record)
        assert "admin_panel" in signals
        assert "non_production" in signals
        assert "debug_enabled" in signals
        assert "sensitive_port" in signals
        assert "dev_port" in signals

    def test_no_signals(self):
        """Should return empty list for clean production host."""
        record = {"host": "www.example.com", "ports": [80, 443]}
        signals = infer_signals(record)
        assert signals == []


class TestReconNormalizeAgent:
    """Test ReconNormalizeAgent functionality."""

    def test_initialization(self):
        """Should initialize with correct name."""
        agent = ReconNormalizeAgent()
        assert agent.name == "recon_normalize"

    def test_normalize_basic_record(self):
        """Should normalize a basic recon record."""
        agent = ReconNormalizeAgent()

        # Create input artifact with raw findings
        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={
                "findings": [
                    {
                        "host": "api.example.com",
                        "status": 200,
                        "title": "API Docs",
                        "ip": "192.168.1.20",
                        "ports": [443, 8080],
                        "headers": {"server": "nginx"},
                    }
                ]
            },
            success=True,
        )

        result = agent.run(input_artifact)

        assert result.success is True
        assert "normalized" in result.output
        assert result.output["total_records"] == 1
        assert result.output["skipped"] == 0

        normalized = result.output["normalized"][0]
        assert normalized["host"] == "api.example.com"
        assert normalized["status"] == 200
        assert normalized["title"] == "API Docs"
        assert normalized["ip"] == "192.168.1.20"
        assert normalized["ports"] == [443, 8080]
        assert normalized["path"] == "/"  # Default
        assert "ts" in normalized
        assert isinstance(normalized["signals"], list)

    def test_normalize_with_signals(self):
        """Should infer signals during normalization."""
        agent = ReconNormalizeAgent()

        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={
                "findings": [
                    {
                        "host": "admin.staging.example.com",
                        "status": 403,
                        "ports": [22],
                        "headers": {"x-debug-mode": "enabled"},
                    }
                ]
            },
            success=True,
        )

        result = agent.run(input_artifact)
        normalized = result.output["normalized"][0]

        assert "admin_panel" in normalized["signals"]
        assert "non_production" in normalized["signals"]
        assert "sensitive_port" in normalized["signals"]
        assert "debug_enabled" in normalized["signals"]

    def test_normalize_minimal_record(self):
        """Should handle records with only required fields."""
        agent = ReconNormalizeAgent()

        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={"findings": [{"host": "example.com"}]},
            success=True,
        )

        result = agent.run(input_artifact)
        normalized = result.output["normalized"][0]

        assert normalized["host"] == "example.com"
        assert normalized["status"] == 0  # Default
        assert normalized["title"] == ""  # Default
        assert normalized["ip"] == "unknown"  # Default
        assert normalized["ports"] == []  # Default
        assert normalized["headers"] == {}  # Default
        assert normalized["path"] == "/"  # Default

    def test_skip_invalid_records(self):
        """Should skip records missing required fields."""
        agent = ReconNormalizeAgent()

        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={
                "findings": [
                    {"host": "valid.example.com"},
                    {"status": 200},  # Missing host
                    {"title": "Test"},  # Missing host
                ]
            },
            success=True,
        )

        result = agent.run(input_artifact)

        assert result.output["total_records"] == 1
        assert result.output["skipped"] == 2
        assert result.output["normalized"][0]["host"] == "valid.example.com"

    def test_empty_input(self):
        """Should handle empty findings list."""
        agent = ReconNormalizeAgent()

        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={"findings": []},
            success=True,
        )

        result = agent.run(input_artifact)

        assert result.success is True
        assert result.output["normalized"] == []
        assert result.output["total_records"] == 0
        assert result.output["skipped"] == 0

    def test_no_input_artifact(self):
        """Should handle None input artifact."""
        agent = ReconNormalizeAgent()
        result = agent.run(None)

        assert result.success is True
        assert result.output["normalized"] == []
        assert result.output["total_records"] == 0

    def test_schema_version(self):
        """Should include schema version in output."""
        agent = ReconNormalizeAgent()

        input_artifact = PipelineArtifact(
            run_id="test-123",
            stage="recon",
            input={},
            output={"findings": [{"host": "example.com"}]},
            success=True,
        )

        result = agent.run(input_artifact)
        assert "schema_version" in result.output
        assert result.output["schema_version"] == "1.0.0"
