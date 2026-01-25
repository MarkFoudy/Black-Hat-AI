"""
Reconnaissance normalization agent.

From Listing 3.6 in Black Hat AI.

The ReconNormalizeAgent normalizes raw reconnaissance data into a
predictable artifact schema. It does NOT score, prioritize, or recommend
actions. Its sole responsibility is to convert raw recon output into
structured data.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..core.artifact import PipelineArtifact
from .base import BaseStage


def infer_signals(record: Dict[str, Any]) -> List[str]:
    """
    Infer signals from raw recon data.

    Signals are derived indicators that may be useful for downstream
    analysis (e.g., "admin_panel", "debug_enabled", "outdated_server").

    Args:
        record: Raw recon record with host, headers, ports, etc.

    Returns:
        List of signal strings
    """
    signals = []

    # Check for admin-related signals
    host = record.get("host", "")
    if "admin" in host.lower():
        signals.append("admin_panel")
    if "staging" in host.lower() or "dev" in host.lower():
        signals.append("non_production")

    # Check headers for debug/development signals
    headers = record.get("headers", {})
    if headers.get("x-debug-mode") == "enabled":
        signals.append("debug_enabled")
    if "x-powered-by" in headers:
        signals.append("tech_disclosure")

    # Check for sensitive ports
    ports = record.get("ports", [])
    sensitive_ports = [22, 3306, 5432, 27017, 6379]  # SSH, MySQL, Postgres, Mongo, Redis
    if any(port in sensitive_ports for port in ports):
        signals.append("sensitive_port")

    # Check for development ports
    dev_ports = [3000, 4000, 5000, 8000, 8080, 9000]
    if any(port in dev_ports for port in ports):
        signals.append("dev_port")

    return signals


class ReconNormalizeAgent(BaseStage):
    """
    Normalization agent that structures raw reconnaissance data.

    From Listing 3.6 in Black Hat AI.

    This agent performs a single, focused task: convert raw, potentially
    inconsistent reconnaissance output into a predictable, structured format
    that downstream agents can reliably consume.

    It does NOT:
    - Score or prioritize findings
    - Make recommendations
    - Perform additional reconnaissance
    - Filter results (except basic validation)

    It DOES:
    - Standardize field names and types
    - Derive basic signals from raw data
    - Add timestamps
    - Validate required fields
    - Ensure consistent schema

    Attributes:
        name: "recon_normalize"

    Example:
        normalizer = ReconNormalizeAgent()

        # Raw input from recon tools
        raw_data = {
            "findings": [
                {"host": "api.example.com", "status": 200, ...},
                {"host": "admin.example.com", "status": 403, ...}
            ]
        }

        artifact = normalizer.run(raw_artifact)
        # artifact.output["normalized"] contains structured records
    """

    name = "recon_normalize"
    description = "Normalizes raw reconnaissance data into structured schema"

    def __init__(self, name: Optional[str] = None, **config):
        """
        Initialize the normalization agent.

        Args:
            name: Optional override for stage name
            **config: Additional configuration
        """
        super().__init__(name=name, **config)

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """
        Normalize raw reconnaissance records.

        Expects input artifact to contain:
            - findings: List of raw recon records

        Each raw record should have:
            - host: hostname (required)
            - status: HTTP status code (optional)
            - title: page title (optional)
            - headers: HTTP headers dict (optional)
            - ports: list of open ports (optional)
            - ip: IP address (optional)

        Produces normalized records with:
            - host: standardized hostname
            - path: URL path (default "/")
            - status: HTTP status code
            - title: page title
            - signals: derived indicator list
            - ts: ISO timestamp

        Args:
            artifact: Previous stage output containing raw findings

        Returns:
            Artifact with normalized records
        """
        if not artifact or "findings" not in artifact.output:
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={
                    "normalized": [],
                    "total_records": 0,
                    "skipped": 0,
                },
                success=True,
            )

        raw_records = artifact.output["findings"]
        normalized = []
        skipped = 0

        for record in raw_records:
            # Validate required fields
            if "host" not in record:
                skipped += 1
                continue

            # Normalize record
            normalized_record = {
                "host": record["host"],
                "path": record.get("path", "/"),
                "status": record.get("status", 0),
                "title": record.get("title", ""),
                "ip": record.get("ip", "unknown"),
                "ports": record.get("ports", []),
                "headers": record.get("headers", {}),
                "signals": infer_signals(record),
                "ts": datetime.utcnow().isoformat(),
            }

            normalized.append(normalized_record)

        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output={
                "normalized": normalized,
                "total_records": len(normalized),
                "skipped": skipped,
                "schema_version": "1.0.0",
            },
            success=True,
        )
