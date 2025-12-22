"""
Listing 4.1: Artifact Helper

Provides the Artifact dataclass for structured reconnaissance data and
JSONL serialization utilities for persistent, append-only logging.

The Artifact class is the connective tissue of the entire pipeline.
Each instance is an auditable record that says, "here's what I did and what I found."
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Iterator, Any
import json
import os

# Output path can be overridden via env var
DEFAULT_OUT = os.environ.get("RECON_OUT", "runs/recon.jsonl")


@dataclass
class Artifact:
    """
    Structured reconnaissance data for a single host.

    This dataclass stores intelligence gathered during passive reconnaissance,
    including DNS data, HTTP metadata, TLS details, and operational notes.

    Attributes:
        schema: Version identifier for the data format (default: "recon-v1")
        host: Fully qualified hostname tested
        a: List of IPv4/IPv6 addresses resolved
        cname: Canonical/primary name (best-effort)
        headers: HTTP response headers (sanitized)
        waf_hint: Header-based heuristic for WAF/CDN presence
        tls: TLS metadata {"alpn": [...], "san": [...]}
        notes: Free-form notes (status codes, errors, robots hints)
        ts: ISO-8601 UTC timestamp set on write
    """

    schema: str = "recon-v1"
    host: str = ""
    a: List[str] = field(default_factory=list)
    cname: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    waf_hint: Optional[bool] = None
    tls: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)
    ts: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artifact":
        """Create an Artifact from a dictionary."""
        return cls(
            schema=data.get("schema", "recon-v1"),
            host=data.get("host", ""),
            a=data.get("a", []),
            cname=data.get("cname"),
            headers=data.get("headers", {}),
            waf_hint=data.get("waf_hint"),
            tls=data.get("tls"),
            notes=data.get("notes", []),
            ts=data.get("ts", ""),
        )


@dataclass
class ScopeArtifact:
    """
    Artifact for recording scope enforcement decisions.

    Used when a host is blocked or allowed based on scope configuration.
    """

    schema: str = "scope-v1"
    host: str = ""
    action: str = ""  # "allowed" or "blocked"
    reason: str = ""
    ts: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary representation."""
        return asdict(self)


def _now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_jsonl(
    artifact: Artifact | ScopeArtifact | Dict[str, Any],
    out_path: str = DEFAULT_OUT,
) -> None:
    """
    Append one artifact as a single JSON line.

    If no timestamp is present, sets a UTC ISO-8601 timestamp.
    Creates parent directories if they don't exist.

    Args:
        artifact: Artifact instance or dictionary to write
        out_path: Output file path (default from RECON_OUT env var)
    """
    if isinstance(artifact, (Artifact, ScopeArtifact)):
        if not artifact.ts:
            artifact.ts = _now_iso()
        data = artifact.to_dict()
    else:
        if "ts" not in artifact or not artifact["ts"]:
            artifact["ts"] = _now_iso()
        data = artifact

    # Create parent directories if needed
    parent_dir = os.path.dirname(out_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(out_path, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")


def iter_jsonl(in_path: str = DEFAULT_OUT) -> Iterator[Dict[str, Any]]:
    """
    Iterate over artifacts in a JSONL file.

    Yields each line as a parsed dictionary. Skips empty lines
    and logs warnings for malformed JSON.

    Args:
        in_path: Input file path

    Yields:
        Dictionary representation of each artifact
    """
    if not os.path.exists(in_path):
        return

    with open(in_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                # Log but don't raise - allow processing to continue
                print(f"Warning: Malformed JSON on line {line_num}: {e}")


def read_jsonl(in_path: str = DEFAULT_OUT) -> List[Dict[str, Any]]:
    """
    Read all artifacts from a JSONL file.

    Args:
        in_path: Input file path

    Returns:
        List of dictionaries, one per artifact
    """
    return list(iter_jsonl(in_path))


def read_artifacts(in_path: str = DEFAULT_OUT) -> List[Artifact]:
    """
    Read all recon artifacts from a JSONL file as Artifact objects.

    Filters to only include recon-v1 schema entries.

    Args:
        in_path: Input file path

    Returns:
        List of Artifact objects
    """
    artifacts = []
    for data in iter_jsonl(in_path):
        if data.get("schema") == "recon-v1":
            artifacts.append(Artifact.from_dict(data))
    return artifacts
