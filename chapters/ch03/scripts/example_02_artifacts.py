#!/usr/bin/env python3
"""
Example 2: Pipeline Artifacts

From Listings 3.2 and 3.3 in Black Hat AI.

Demonstrates how artifacts store state between pipeline stages,
including structure, serialization, and logging.

Run:
    python scripts/example_02_artifacts.py
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.artifact import PipelineArtifact
from src.core.logger import ArtifactLogger


def main():
    """Demonstrate artifact creation, chaining, and logging."""
    print("=" * 60)
    print("Example 2: Pipeline Artifacts")
    print("=" * 60)
    print()

    # Create an artifact (Listing 3.2)
    print("Creating a PipelineArtifact...")
    artifact = PipelineArtifact(
        stage="triage",
        input={"targets": ["admin.example.com", "cdn.example.com"]},
        output={"high_risk": ["admin.example.com"]},
        success=True,
    )

    print(f"Run ID: {artifact.run_id}")
    print(f"Stage: {artifact.stage}")
    print(f"Success: {artifact.success}")
    print(f"Timestamp: {artifact.timestamp}")
    print()

    # Show JSON representation (Listing 3.3)
    print("JSON representation:")
    print("-" * 40)
    print(json.dumps(artifact.to_jsonl_record(), indent=2))
    print()

    # Demonstrate artifact chaining
    print("Chaining artifacts across stages...")
    print("-" * 40)

    # First artifact (recon stage)
    artifact1 = PipelineArtifact(
        stage="recon",
        input={},
        output={"hosts": ["host1.example.com", "host2.example.com"]},
        success=True,
    )
    print(f"Stage 1 (recon): run_id={artifact1.run_id[:8]}...")

    # Second artifact using from_previous (maintains run_id)
    artifact2 = PipelineArtifact.from_previous(
        previous=artifact1,
        stage="triage",
        output={"high_risk": ["host1.example.com"]},
        success=True,
    )
    print(f"Stage 2 (triage): run_id={artifact2.run_id[:8]}... (same!)")

    # Third artifact
    artifact3 = PipelineArtifact.from_previous(
        previous=artifact2,
        stage="report",
        output={"report_path": "report.md"},
        success=True,
    )
    print(f"Stage 3 (report): run_id={artifact3.run_id[:8]}... (same!)")
    print()

    # Demonstrate logging
    print("Logging artifacts to JSONL file...")
    print("-" * 40)

    with ArtifactLogger(run_dir="runs") as logger:
        logger.write_artifact(artifact1)
        logger.write_artifact(artifact2)
        logger.write_artifact(artifact3)
        print(f"Logged to: {logger.file_path}")

    print()
    print("Key Takeaways:")
    print("- Artifacts carry data AND metadata between stages")
    print("- run_id links all artifacts in a single pipeline run")
    print("- JSONL format enables streaming analysis and debugging")

    return 0


if __name__ == "__main__":
    sys.exit(main())
