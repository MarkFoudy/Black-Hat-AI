#!/usr/bin/env python3
"""
Example 3: Pipeline Orchestrator

From Listings 3.4 and 3.7 in Black Hat AI.

Demonstrates the PipelineOrchestrator, which coordinates stage execution,
enforces gates, and manages artifacts automatically.

Run:
    python scripts/example_03_orchestrator.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.orchestrator import PipelineOrchestrator
from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.gates import GlobalGate


def main():
    """Demonstrate the PipelineOrchestrator."""
    print("=" * 60)
    print("Example 3: Pipeline Orchestrator")
    print("=" * 60)
    print()

    # Create agents (Listing 3.13)
    recon_agent = ReconAgent(name="recon")
    triage_agent = TriageAgent(name="triage")
    report_agent = ReportAgent(name="report", output_dir="runs/reports")

    # Create gates
    # Using wide time window to ensure it passes during demo
    gate = GlobalGate(start_hour=0, end_hour=23, enabled=True)

    print("Creating orchestrator with 3 stages and 1 gate...")
    print(f"  Stages: {[a.name for a in [recon_agent, triage_agent, report_agent]]}")
    print(f"  Gates: [{gate}]")
    print()

    # Create orchestrator (Listing 3.4 / 3.14)
    pipeline = PipelineOrchestrator(
        stages=[recon_agent, triage_agent, report_agent],
        gates=[gate],
        run_dir="runs",
    )

    print(f"Run ID: {pipeline.run_id}")
    print()

    # Run the pipeline
    print("Executing pipeline...")
    print("-" * 40)

    try:
        final_artifact = pipeline.run()

        print()
        print("Pipeline completed successfully!")
        print(f"Artifact log: {pipeline.get_artifact_path()}")

        if final_artifact:
            report_path = final_artifact.output.get("report_path")
            if report_path:
                print(f"Report saved: {report_path}")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        return 1

    print()
    print("Key Takeaways:")
    print("- Orchestrator handles stage sequencing automatically")
    print("- Gates are checked before each stage executes")
    print("- All artifacts are logged with the same run_id")
    print("- Failed stages can be recovered with checkpointing (see example_05)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
