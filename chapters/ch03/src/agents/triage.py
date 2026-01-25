"""
Triage agent for risk scoring and prioritization.

From Listing 3.7 in Black Hat AI.

The TriageAgent analyzes normalized reconnaissance data and ranks targets
by exploitability and risk level. It consumes structured output from
ReconNormalizeAgent, not raw recon data.
"""

from typing import Optional, List, Dict, Any

from ..core.artifact import PipelineArtifact
from .base import BaseStage


# Risk scoring rules
HIGH_RISK_PORTS = {22, 23, 3389, 5432, 3306, 27017, 6379}  # SSH, Telnet, RDP, DBs
MEDIUM_RISK_PORTS = {21, 25, 110, 143, 8080, 8443}  # FTP, Mail, Alt HTTP
HIGH_RISK_HEADERS = {"x-debug-mode", "x-powered-by", "server"}
HIGH_RISK_KEYWORDS = {"admin", "staging", "dev", "test", "debug"}


class TriageAgent(BaseStage):
    """
    Triage agent that scores and prioritizes normalized findings.

    From Listing 3.7 in Black Hat AI.

    This agent consumes NORMALIZED data from ReconNormalizeAgent and
    assigns risk scores based on:
    - Open ports (databases, remote access, debug services)
    - HTTP headers (debug modes, version disclosure)
    - Hostname patterns (admin, staging, dev systems)
    - Derived signals from normalization

    Findings are categorized as high, medium, or low risk.

    This agent does NOT:
    - Normalize or validate input data
    - Perform additional reconnaissance
    - Execute exploits or make modifications

    Attributes:
        name: "triage"
        risk_threshold: Minimum score for high-risk classification

    Example:
        # After ReconNormalizeAgent
        triage = TriageAgent(risk_threshold=5)
        artifact = triage.run(normalized_artifact)
        print(artifact.output["high_risk"])
    """

    name = "triage"
    description = "Scores and prioritizes findings by risk level"

    def __init__(
        self,
        risk_threshold: int = 5,
        name: Optional[str] = None,
        **config,
    ):
        """
        Initialize the triage agent.

        Args:
            risk_threshold: Score threshold for high-risk classification
            name: Optional override for stage name
            **config: Additional configuration
        """
        super().__init__(name=name, **config)
        self.risk_threshold = risk_threshold

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """
        Analyze and score normalized reconnaissance findings.

        Expects input from ReconNormalizeAgent with "normalized" key.
        Falls back to "findings" for backward compatibility.

        Args:
            artifact: Normalized recon artifact

        Returns:
            Artifact with scored and categorized findings
        """
        if not artifact:
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={"error": "No artifact provided", "high_risk": [], "medium_risk": [], "low_risk": []},
                success=False,
                error="No artifact provided",
            )

        # Prefer "normalized" key from ReconNormalizeAgent, fall back to "findings"
        findings = artifact.output.get("normalized") or artifact.output.get("findings")

        if not findings:
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={"error": "No findings to triage", "high_risk": [], "medium_risk": [], "low_risk": []},
                success=False,
                error="No findings provided",
            )
        scored_findings = []

        for finding in findings:
            score = self._calculate_risk_score(finding)
            scored_finding = {
                **finding,
                "risk_score": score,
                "risk_level": self._score_to_level(score),
            }
            scored_findings.append(scored_finding)

        # Sort by risk score (highest first)
        scored_findings.sort(key=lambda x: x["risk_score"], reverse=True)

        # Categorize findings
        high_risk = [f["host"] for f in scored_findings if f["risk_level"] == "high"]
        medium_risk = [f["host"] for f in scored_findings if f["risk_level"] == "medium"]
        low_risk = [f["host"] for f in scored_findings if f["risk_level"] == "low"]

        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output={
                "scored_findings": scored_findings,
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk,
                "summary": {
                    "total": len(scored_findings),
                    "high": len(high_risk),
                    "medium": len(medium_risk),
                    "low": len(low_risk),
                },
            },
            success=True,
        )

    def _calculate_risk_score(self, finding: Dict[str, Any]) -> int:
        """
        Calculate risk score for a finding.

        Scoring:
        - High-risk ports: +3 each
        - Medium-risk ports: +1 each
        - Risky headers: +2 each
        - Risky keywords in hostname: +2 each

        Args:
            finding: Single finding dictionary

        Returns:
            Integer risk score
        """
        score = 0
        host = finding.get("host", "").lower()
        ports = set(finding.get("ports", []))
        headers = finding.get("headers", {})

        # Score ports
        score += len(ports & HIGH_RISK_PORTS) * 3
        score += len(ports & MEDIUM_RISK_PORTS) * 1

        # Score headers
        for header_name in headers:
            if header_name.lower() in HIGH_RISK_HEADERS:
                score += 2
            # Extra points for debug mode
            if "debug" in header_name.lower():
                score += 3

        # Score hostname keywords
        for keyword in HIGH_RISK_KEYWORDS:
            if keyword in host:
                score += 2

        return score

    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to risk level."""
        if score >= self.risk_threshold:
            return "high"
        elif score >= self.risk_threshold // 2:
            return "medium"
        else:
            return "low"
