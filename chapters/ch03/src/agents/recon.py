"""
Reconnaissance agent for raw target discovery.

The ReconAgent performs passive reconnaissance to discover targets and
collect raw information about the attack surface. This agent focuses
solely on data collection without normalization, scoring, or analysis.

Output is passed to ReconNormalizeAgent for schema standardization.
"""

from typing import Optional, List, Dict, Any

from ..core.artifact import PipelineArtifact
from .base import BaseStage


# Synthetic recon data for demonstration
SYNTHETIC_RECON_DATA = {
    "example.com": {
        "subdomains": [
            {"host": "admin.example.com", "ip": "192.168.1.10"},
            {"host": "api.example.com", "ip": "192.168.1.20"},
            {"host": "cdn.example.com", "ip": "192.168.1.30"},
            {"host": "staging.example.com", "ip": "192.168.1.40"},
        ],
        "open_ports": {
            "admin.example.com": [22, 80, 443],
            "api.example.com": [443, 8080],
            "cdn.example.com": [80, 443],
            "staging.example.com": [22, 80, 443, 3000, 5432],
        },
        "http_headers": {
            "admin.example.com": {
                "server": "nginx/1.18.0",
                "x-powered-by": "PHP/7.4",
            },
            "api.example.com": {
                "server": "gunicorn",
                "x-powered-by": "Express",
            },
            "staging.example.com": {
                "server": "Apache/2.4.41",
                "x-debug-mode": "enabled",
            },
        },
    }
}


class ReconAgent(BaseStage):
    """
    Reconnaissance agent that collects raw target data.

    This agent performs passive reconnaissance tasks to collect raw data:
    - Subdomain enumeration
    - Port discovery
    - HTTP header collection
    - Technology fingerprinting

    This agent does NOT:
    - Normalize or validate data structure
    - Infer signals or derive indicators
    - Score or prioritize findings
    - Make recommendations

    For demonstration, this uses synthetic data. In production, integrate
    with real recon tools (subfinder, httpx, nmap, etc.).

    Output is raw findings that require normalization by ReconNormalizeAgent
    before being consumed by downstream agents like TriageAgent.

    Attributes:
        name: "recon"
        targets: List of root domains to scan

    Example:
        recon = ReconAgent(targets=["example.com"])
        artifact = recon.run(None)
        # Raw findings ready for normalization
        print(artifact.output["findings"])
    """

    name = "recon"
    description = "Collects raw reconnaissance data from targets"

    def __init__(
        self,
        targets: Optional[List[str]] = None,
        name: Optional[str] = None,
        **config,
    ):
        """
        Initialize the recon agent.

        Args:
            targets: List of root domains to scan
            name: Optional override for stage name
            **config: Additional configuration
        """
        super().__init__(name=name, **config)
        self.targets = targets or ["example.com"]

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """
        Execute reconnaissance on configured targets.

        Collects raw data from recon tools. Output should be passed to
        ReconNormalizeAgent for schema standardization before triage.

        Args:
            artifact: Previous stage output (typically None for recon)

        Returns:
            Artifact containing raw findings (hosts, ports, headers)
        """
        # Get targets from artifact if provided
        if artifact and "targets" in artifact.output:
            targets = artifact.output["targets"]
        else:
            targets = self.targets

        findings = []

        for domain in targets:
            # Use synthetic data or perform real recon
            data = SYNTHETIC_RECON_DATA.get(domain, self._empty_recon())

            for subdomain in data.get("subdomains", []):
                host = subdomain["host"]
                finding = {
                    "host": host,
                    "ip": subdomain.get("ip", "unknown"),
                    "ports": data.get("open_ports", {}).get(host, []),
                    "headers": data.get("http_headers", {}).get(host, {}),
                    "domain": domain,
                }
                findings.append(finding)

        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output={
                "targets": targets,
                "findings": findings,
                "total_hosts": len(findings),
            },
            success=True,
        )

    def _empty_recon(self) -> Dict[str, Any]:
        """Return empty recon structure for unknown domains."""
        return {
            "subdomains": [],
            "open_ports": {},
            "http_headers": {},
        }
