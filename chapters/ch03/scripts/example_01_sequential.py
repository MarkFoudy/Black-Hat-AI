#!/usr/bin/env python3
"""
Example 1: Basic Sequential Pipeline

From Section 3.3.1 in Black Hat AI.

Demonstrates the simplest multi-agent pattern: a sequential pipeline
where each stage passes its output to the next.

Run:
    python scripts/example_01_sequential.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agents import ReconAgent, ReconNormalizeAgent, TriageAgent, ReportAgent
from src.core.artifact import PipelineArtifact


def main():
    """Run a basic sequential pipeline without orchestration."""
    print("=" * 60)
    print("Example 1: Basic Sequential Pipeline")
    print("=" * 60)
    print()

    # Create agents
    recon_agent = ReconAgent(name="recon")
    normalize_agent = ReconNormalizeAgent(name="recon_normalize")
    triage_agent = TriageAgent(name="triage")
    report_agent = ReportAgent(name="report")

    print("Pipeline: Recon -> Normalize -> Triage -> Report")
    print()

    # Execute sequentially (manual orchestration)
    print("[1/4] Running Recon Agent...")
    recon_artifact = recon_agent.run(None)
    print(f"      Found {recon_artifact.output['total_hosts']} hosts (raw)")
    print()

    print("[2/4] Running Normalization Agent...")
    normalize_artifact = normalize_agent.run(recon_artifact)
    print(f"      Normalized {normalize_artifact.output['total_records']} records")
    print(f"      Skipped {normalize_artifact.output['skipped']} invalid records")
    print()

    print("[3/4] Running Triage Agent...")
    triage_artifact = triage_agent.run(normalize_artifact)
    summary = triage_artifact.output.get("summary", {})
    print(f"      High risk: {summary.get('high', 0)}")
    print(f"      Medium risk: {summary.get('medium', 0)}")
    print(f"      Low risk: {summary.get('low', 0)}")
    print()

    print("[4/4] Running Report Agent...")
    report_artifact = report_agent.run(triage_artifact)
    print(f"      Report generated at: {report_artifact.output.get('generated_at')}")
    print()

    # Show a snippet of the report
    print("=" * 60)
    print("Report Preview:")
    print("=" * 60)
    report_content = report_artifact.output.get("report_content", "")
    # Print first 20 lines
    for line in report_content.split("\n")[:20]:
        print(line)
    print("...")
    print()

    print("Sequential pipeline complete!")
    print()
    print("Key Takeaway: Each agent receives the previous agent's artifact")
    print("and produces a new artifact for the next stage.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
