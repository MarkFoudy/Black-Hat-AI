"""
Report agent for generating human-readable summaries.

From Listing 3.8 in Black Hat AI.

The ReportAgent consumes triage output and produces markdown reports
suitable for executive summaries and technical documentation.
"""

from typing import Optional
from datetime import datetime
import os

from ..core.artifact import PipelineArtifact
from .base import BaseStage


class ReportAgent(BaseStage):
    """
    Report agent that generates markdown summaries of findings.

    From Listing 3.8 in Black Hat AI.

    This agent transforms structured triage data into human-readable
    reports including:
    - Executive summary with risk counts
    - High-risk findings table
    - Detailed findings by host
    - Recommendations

    Attributes:
        name: "report"
        output_dir: Directory to save report files
        include_details: Whether to include full finding details

    Example:
        report = ReportAgent(output_dir="reports")
        artifact = report.run(triage_artifact)
        print(artifact.output["report_content"])
    """

    name = "report"
    description = "Generates markdown summary reports"

    def __init__(
        self,
        output_dir: Optional[str] = None,
        include_details: bool = True,
        name: Optional[str] = None,
        **config,
    ):
        """
        Initialize the report agent.

        Args:
            output_dir: Directory to save reports (optional)
            include_details: Include detailed findings (default: True)
            name: Optional override for stage name
            **config: Additional configuration
        """
        super().__init__(name=name, **config)
        self.output_dir = output_dir
        self.include_details = include_details

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """
        Generate a markdown report from triage findings.

        Args:
            artifact: Triage artifact containing scored findings

        Returns:
            Artifact with report content and optional file path
        """
        if not artifact:
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={"error": "No triage data to report"},
                success=False,
                error="No input artifact",
            )

        # Generate report content
        report = self._generate_report(artifact)

        output = {
            "report_content": report,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Save to file if output_dir configured
        if self.output_dir:
            output["report_path"] = self._save_report(report, artifact.run_id)

        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output=output,
            success=True,
        )

    def _generate_report(self, artifact: PipelineArtifact) -> str:
        """Generate markdown report content."""
        data = artifact.output
        lines = []

        # Header
        lines.append("# Security Reconnaissance Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append(f"**Run ID:** `{artifact.run_id}`")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")

        summary = data.get("summary", {})
        high_count = summary.get("high", len(data.get("high_risk", [])))
        medium_count = summary.get("medium", len(data.get("medium_risk", [])))
        low_count = summary.get("low", len(data.get("low_risk", [])))
        total = summary.get("total", high_count + medium_count + low_count)

        lines.append(f"| Risk Level | Count |")
        lines.append(f"|------------|-------|")
        lines.append(f"| High       | {high_count}     |")
        lines.append(f"| Medium     | {medium_count}     |")
        lines.append(f"| Low        | {low_count}     |")
        lines.append(f"| **Total**  | **{total}** |")
        lines.append("")

        # High-Risk Findings
        high_risk = data.get("high_risk", [])
        if high_risk:
            lines.append("## High-Risk Findings")
            lines.append("")
            lines.append("The following targets require immediate attention:")
            lines.append("")
            for host in high_risk:
                lines.append(f"- `{host}`")
            lines.append("")

        # Detailed Findings
        if self.include_details:
            scored_findings = data.get("scored_findings", [])
            if scored_findings:
                lines.append("## Detailed Findings")
                lines.append("")

                for finding in scored_findings:
                    host = finding.get("host", "unknown")
                    risk = finding.get("risk_level", "unknown")
                    score = finding.get("risk_score", 0)

                    risk_emoji = {"high": "!!", "medium": "!", "low": "o"}.get(risk, "?")

                    lines.append(f"### [{risk_emoji}] {host}")
                    lines.append("")
                    lines.append(f"- **Risk Level:** {risk.upper()} (score: {score})")
                    lines.append(f"- **IP:** {finding.get('ip', 'unknown')}")

                    ports = finding.get("ports", [])
                    if ports:
                        lines.append(f"- **Open Ports:** {', '.join(map(str, ports))}")

                    headers = finding.get("headers", {})
                    if headers:
                        lines.append("- **HTTP Headers:**")
                        for k, v in headers.items():
                            lines.append(f"  - `{k}`: `{v}`")

                    lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        if high_count > 0:
            lines.append("1. **Immediately review** all high-risk findings")
            lines.append("2. **Disable debug modes** on staging/development systems")
            lines.append("3. **Restrict access** to administrative interfaces")
            lines.append("4. **Update software** to remove version disclosure headers")
        else:
            lines.append("No high-risk findings detected. Continue monitoring.")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("*Report generated by Black Hat AI Multi-Agent Pipeline*")

        return "\n".join(lines)

    def _save_report(self, content: str, run_id: str) -> str:
        """Save report to file and return path."""
        os.makedirs(self.output_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}_{run_id[:8]}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath
