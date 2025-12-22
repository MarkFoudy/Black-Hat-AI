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

from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.core.artifact import PipelineArtifact


def main():
    """Run a basic sequential pipeline without orchestration."""
    print("=" * 60)
    print("Example 1: Basic Sequential Pipeline")
    print("=" * 60)
    print()

    # Create agents (Listing 3.13 pattern)
    recon_agent = ReconAgent(name="recon")
    triage_agent = TriageAgent(name="triage")
    report_agent = ReportAgent(name="report")

    print("Pipeline: Recon -> Triage -> Report")
    print()

    # Execute sequentially (manual orchestration)
    print("[1/3] Running Recon Agent...")
    recon_artifact = recon_agent.run(None)
    print(f"      Found {recon_artifact.output['total_hosts']} hosts")
    print()

    print("[2/3] Running Triage Agent...")
    triage_artifact = triage_agent.run(recon_artifact)
    summary = triage_artifact.output.get("summary", {})
    print(f"      High risk: {summary.get('high', 0)}")
    print(f"      Medium risk: {summary.get('medium', 0)}")
    print(f"      Low risk: {summary.get('low', 0)}")
    print()

    print("[3/3] Running Report Agent...")
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
