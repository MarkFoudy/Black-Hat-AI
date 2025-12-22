#!/usr/bin/env python3
"""
Example 7: Capstone - Complete Recon-Triage-Report Pipeline

From Section 3.9 and Listings 3.13-3.17 in Black Hat AI.

This capstone brings together all concepts:
- Multi-agent orchestration
- Artifact management
- Safety gates
- Error handling
- Visualization

Run:
    python scripts/example_07_capstone.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.orchestrator import PipelineOrchestrator
from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.gates import GlobalGate, EnvironmentGate, ScopeGate
from src.visualization import export_mermaid
from src.visualization.trace import get_run_summary


def main():
    """Run the complete capstone pipeline."""
    print("=" * 60)
    print("Capstone: Recon -> Triage -> Report Pipeline")
    print("From Section 3.9 in Black Hat AI")
    print("=" * 60)
    print()

    # Step 1: Define agents (Listing 3.13)
    print("Step 1: Creating agents")
    print("-" * 40)

    recon_agent = ReconAgent(name="recon", targets=["example.com"])
    triage_agent = TriageAgent(name="triage", risk_threshold=5)
    report_agent = ReportAgent(name="report", output_dir="runs/reports")

    print(f"  - {recon_agent}")
    print(f"  - {triage_agent}")
    print(f"  - {report_agent}")
    print()

    # Step 2: Configure gates (Listing 3.16)
    print("Step 2: Configuring safety gates")
    print("-" * 40)

    gates = [
        GlobalGate(start_hour=0, end_hour=23),  # Allow all hours for demo
        EnvironmentGate(prohibited_patterns=["prod", "payment"], check_hostname=False),
        ScopeGate(authorized_domains=["example.com"]),
    ]

    for gate in gates:
        print(f"  - {gate}")
    print()

    # Step 3: Create orchestrator (Listing 3.14)
    print("Step 3: Creating orchestrator")
    print("-" * 40)

    pipeline = PipelineOrchestrator(
        stages=[recon_agent, triage_agent, report_agent],
        gates=gates,
        run_dir="runs",
    )

    print(f"  Run ID: {pipeline.run_id}")
    print(f"  Artifact path: {pipeline.get_artifact_path()}")
    print()

    # Step 4: Visualize pipeline structure (Listing 3.17)
    print("Step 4: Pipeline structure (Mermaid)")
    print("-" * 40)
    export_mermaid([recon_agent, triage_agent, report_agent])
    print()

    # Step 5: Execute pipeline (Listing 3.16)
    print("Step 5: Executing pipeline")
    print("-" * 40)

    try:
        final_artifact = pipeline.run()
        print()
        print("Pipeline completed successfully!")

    except Exception as e:
        print(f"\n[Recover] Pipeline halted: {e}")
        return 1

    # Step 6: Inspect results (Listing 3.15)
    print()
    print("Step 6: Inspecting results")
    print("-" * 40)

    if final_artifact:
        # Show report location
        report_path = final_artifact.output.get("report_path")
        if report_path:
            print(f"  Report saved: {report_path}")

        # Show triage summary (from the artifact's input, which was triage output)
        triage_output = final_artifact.input
        if "summary" in triage_output:
            summary = triage_output["summary"]
            print(f"\n  Triage Summary:")
            print(f"    High risk:   {summary.get('high', 0)} hosts")
            print(f"    Medium risk: {summary.get('medium', 0)} hosts")
            print(f"    Low risk:    {summary.get('low', 0)} hosts")

        if "high_risk" in triage_output:
            high_risk = triage_output["high_risk"]
            if high_risk:
                print(f"\n  High-risk targets requiring attention:")
                for host in high_risk:
                    print(f"    - {host}")

    print()

    # Step 7: Show artifact log
    print("Step 7: Artifact log preview")
    print("-" * 40)

    import json
    artifact_path = pipeline.get_artifact_path()
    print(f"  Reading: {artifact_path}")
    print()

    with open(artifact_path, "r") as f:
        for i, line in enumerate(f):
            if line.strip() and i < 5:  # Show first 5 entries
                rec = json.loads(line)
                print(f"  {rec.get('stage', '?'):12} | success={rec.get('success', '?')}")

    print()
    print("=" * 60)
    print("Capstone Complete!")
    print("=" * 60)
    print()
    print("You have built a multi-agent security pipeline that:")
    print("  1. Discovers targets through reconnaissance")
    print("  2. Triages findings by risk level")
    print("  3. Generates executive reports")
    print("  4. Enforces safety gates at each stage")
    print("  5. Logs all actions for audit and replay")
    print()
    print("Next steps:")
    print("  - Add real reconnaissance tools (subfinder, httpx)")
    print("  - Implement LLM-powered analysis with adapters")
    print("  - Add more specialized agents (exploit, bypass)")
    print("  - Deploy with monitoring and alerting")

    return 0


if __name__ == "__main__":
    sys.exit(main())
