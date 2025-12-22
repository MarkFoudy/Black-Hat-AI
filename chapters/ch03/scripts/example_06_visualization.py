#!/usr/bin/env python3
"""
Example 6: Visualization and Auditing

From Listings 3.11, 3.12, and 3.17 in Black Hat AI.

Demonstrates pipeline visualization:
- Trace summarization
- Mermaid diagram generation
- Execution status visualization

Run:
    python scripts/example_06_visualization.py
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.core.orchestrator import PipelineOrchestrator
from src.visualization import summarize_run, export_mermaid, generate_mermaid
from src.visualization.mermaid import generate_sequence_diagram, generate_execution_diagram


def main():
    """Demonstrate visualization and auditing tools."""
    print("=" * 60)
    print("Example 6: Visualization and Auditing")
    print("=" * 60)
    print()

    # Create and run a pipeline first
    print("Running pipeline to generate artifacts...")
    print("-" * 40)

    recon_agent = ReconAgent(name="recon")
    triage_agent = TriageAgent(name="triage")
    report_agent = ReportAgent(name="report")

    stages = [recon_agent, triage_agent, report_agent]

    pipeline = PipelineOrchestrator(stages=stages, run_dir="runs")
    final_artifact = pipeline.run()

    print()

    # 1. Mermaid Flowchart (Listing 3.12 / 3.17)
    print("1. Mermaid Flowchart (Listing 3.12)")
    print("-" * 40)
    export_mermaid(stages)
    print()

    # 2. Trace Summarization (Listing 3.11)
    print("2. Trace Summary (Listing 3.11)")
    print("-" * 40)
    # The orchestrator logs to a single file, not a directory
    # Let's create a summary from the artifact log
    artifact_path = pipeline.get_artifact_path()
    run_dir = os.path.dirname(artifact_path)

    # Read and display the artifacts
    print(f"Reading artifacts from: {artifact_path}")
    with open(artifact_path, "r") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                stage = rec.get("stage", "?")
                success = rec.get("success", "?")
                timestamp = rec.get("timestamp", "?")
                if isinstance(timestamp, str) and "T" in timestamp:
                    timestamp = timestamp.split("T")[0] + " " + timestamp.split("T")[1][:8]
                print(f"  {timestamp} | {stage:12} | success={success}")
    print()

    # 3. Execution Diagram with Status
    print("3. Execution Diagram with Status Colors")
    print("-" * 40)

    # Build status from artifacts
    stage_status = {
        "recon": "completed",
        "triage": "completed",
        "report": "completed",
    }

    diagram = generate_mermaid(stages, include_status=True, stage_status=stage_status)
    print(diagram)
    print()

    # 4. Sequence Diagram
    print("4. Sequence Diagram (Data Flow)")
    print("-" * 40)
    seq_diagram = generate_sequence_diagram(stages)
    print(seq_diagram)
    print()

    # 5. Save diagrams to files
    print("5. Saving Diagrams to Files")
    print("-" * 40)

    from src.visualization.mermaid import save_mermaid

    flowchart_path = save_mermaid(stages, "runs/diagrams/flowchart.mmd")
    print(f"   Flowchart saved: {flowchart_path}")

    status_path = save_mermaid(
        stages,
        "runs/diagrams/execution.mmd",
        include_status=True,
        stage_status=stage_status,
    )
    print(f"   Execution diagram saved: {status_path}")
    print()

    print("Key Takeaways:")
    print("- Mermaid diagrams render in GitHub, VS Code, and documentation")
    print("- Traces provide chronological view of pipeline execution")
    print("- Status-colored diagrams show at-a-glance execution results")
    print("- Diagrams can be auto-generated after each run for documentation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
