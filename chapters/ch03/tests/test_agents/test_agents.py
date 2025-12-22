"""
Tests for pipeline agents (Recon, Triage, Report).

From Listing 3.13 in Black Hat AI.
"""

import pytest
import os
import shutil

from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.core.artifact import PipelineArtifact


class TestReconAgent:
    """Tests for ReconAgent."""

    def test_create_recon_agent(self):
        """Test agent creation."""
        agent = ReconAgent(targets=["example.com"])

        assert agent.name == "recon"
        assert agent.targets == ["example.com"]

    def test_run_returns_findings(self):
        """Test that recon produces findings."""
        agent = ReconAgent(targets=["example.com"])
        artifact = agent.run(None)

        assert artifact.stage == "recon"
        assert artifact.success is True
        assert "findings" in artifact.output
        assert "total_hosts" in artifact.output

    def test_synthetic_data(self):
        """Test that synthetic data is returned for example.com."""
        agent = ReconAgent(targets=["example.com"])
        artifact = agent.run(None)

        findings = artifact.output["findings"]
        assert len(findings) > 0

        # Check finding structure
        finding = findings[0]
        assert "host" in finding
        assert "ports" in finding
        assert "headers" in finding


class TestTriageAgent:
    """Tests for TriageAgent."""

    def test_create_triage_agent(self):
        """Test agent creation."""
        agent = TriageAgent(risk_threshold=5)

        assert agent.name == "triage"
        assert agent.risk_threshold == 5

    def test_triage_scores_findings(self):
        """Test that triage scores findings."""
        # Create mock recon artifact
        recon_artifact = PipelineArtifact(
            stage="recon",
            input={},
            output={
                "findings": [
                    {"host": "admin.example.com", "ports": [22, 443], "headers": {}},
                    {"host": "cdn.example.com", "ports": [80], "headers": {}},
                ]
            },
            success=True,
        )

        agent = TriageAgent()
        artifact = agent.run(recon_artifact)

        assert artifact.stage == "triage"
        assert artifact.success is True
        assert "scored_findings" in artifact.output
        assert "high_risk" in artifact.output
        assert "summary" in artifact.output

    def test_risk_scoring(self):
        """Test that high-risk ports increase score."""
        # Host with SSH (port 22) should score higher
        recon_artifact = PipelineArtifact(
            stage="recon",
            input={},
            output={
                "findings": [
                    {"host": "admin.example.com", "ports": [22, 3389], "headers": {"x-debug-mode": "on"}},
                    {"host": "www.example.com", "ports": [80, 443], "headers": {}},
                ]
            },
            success=True,
        )

        agent = TriageAgent(risk_threshold=3)
        artifact = agent.run(recon_artifact)

        scored = artifact.output["scored_findings"]
        admin_finding = next(f for f in scored if "admin" in f["host"])
        www_finding = next(f for f in scored if "www" in f["host"])

        assert admin_finding["risk_score"] > www_finding["risk_score"]

    def test_empty_findings(self):
        """Test triage with no findings."""
        recon_artifact = PipelineArtifact(
            stage="recon",
            input={},
            output={"findings": []},
            success=True,
        )

        agent = TriageAgent()
        artifact = agent.run(recon_artifact)

        assert artifact.output["summary"]["total"] == 0


class TestReportAgent:
    """Tests for ReportAgent."""

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory."""
        return str(tmp_path / "reports")

    def test_create_report_agent(self, output_dir):
        """Test agent creation."""
        agent = ReportAgent(output_dir=output_dir)

        assert agent.name == "report"
        assert agent.output_dir == output_dir

    def test_generate_markdown_report(self, output_dir):
        """Test that report generates markdown."""
        triage_artifact = PipelineArtifact(
            stage="triage",
            input={},
            output={
                "high_risk": ["admin.example.com"],
                "medium_risk": ["api.example.com"],
                "low_risk": ["cdn.example.com"],
                "summary": {"total": 3, "high": 1, "medium": 1, "low": 1},
                "scored_findings": [],
            },
            success=True,
        )

        agent = ReportAgent(output_dir=output_dir)
        artifact = agent.run(triage_artifact)

        assert artifact.success is True
        assert "report_content" in artifact.output

        content = artifact.output["report_content"]
        assert "# Security Reconnaissance Report" in content
        assert "Executive Summary" in content
        assert "High-Risk Findings" in content

    def test_save_report_to_file(self, output_dir):
        """Test that report is saved to file."""
        triage_artifact = PipelineArtifact(
            stage="triage",
            input={},
            output={
                "high_risk": [],
                "medium_risk": [],
                "low_risk": [],
                "summary": {"total": 0, "high": 0, "medium": 0, "low": 0},
            },
            success=True,
        )

        agent = ReportAgent(output_dir=output_dir)
        artifact = agent.run(triage_artifact)

        assert "report_path" in artifact.output
        report_path = artifact.output["report_path"]
        assert os.path.exists(report_path)
        assert report_path.endswith(".md")
