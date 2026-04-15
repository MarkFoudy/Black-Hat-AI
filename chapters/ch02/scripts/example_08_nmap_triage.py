#!/usr/bin/env python3
"""
NMAP Triage Agent

From Section 2.6 in Black Hat AI Chapter 2.

Demonstrates:
- Reading saved reconnaissance data (no live scanning)
- Parsing nmap output
- Prioritizing targets based on risk indicators
- Generating actionable triage reports
- Complete artifact logging

This agent never touches the network. It works entirely on saved output files,
making it safe for analysis and triage workflows.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.logger import ArtifactLogger
from src.tools.nmap_parser import NmapParserTool
from src.tools.triage_analyzer import TriageAnalyzerTool


class NmapTriageAgent:
    """
    Agent for triaging nmap reconnaissance data.

    This agent demonstrates the complete triage workflow:
    1. Parse - Convert nmap output to structured data
    2. Analyze - Score and prioritize hosts
    3. Report - Generate human-readable findings

    All operations are offline. No network requests are made.
    """

    def __init__(self, logger):
        """
        Initialize the triage agent.

        Args:
            logger: ArtifactLogger instance for recording actions
        """
        self.tools = {
            "parse_nmap": NmapParserTool(),
            "analyze_triage": TriageAnalyzerTool()
        }
        self.logger = logger

    def run(self, nmap_output: str) -> dict:
        """
        Run the complete triage workflow.

        Args:
            nmap_output: Text content from nmap scan

        Returns:
            Dictionary with analysis results and formatted report
        """
        # Step 1: Parse nmap output
        print("Step 1: Parsing nmap output...")
        parsed = self.tools["parse_nmap"].invoke({"text": nmap_output})
        self.logger.write({
            "stage": "parse",
            "tool": "parse_nmap",
            "output": parsed
        })
        print(f"  ✓ Parsed {len(parsed['hosts'])} hosts")
        print()

        # Step 2: Analyze and prioritize
        print("Step 2: Analyzing targets...")
        analysis = self.tools["analyze_triage"].invoke(parsed)
        self.logger.write({
            "stage": "analyze",
            "tool": "analyze_triage",
            "output": analysis
        })
        print(f"  ✓ High priority: {analysis['summary']['high_count']}")
        print(f"  ✓ Medium priority: {analysis['summary']['medium_count']}")
        print(f"  ✓ Low priority: {analysis['summary']['low_count']}")
        print()

        # Step 3: Generate report
        print("Step 3: Generating triage report...")
        report = self._generate_report(analysis)
        self.logger.write({
            "stage": "report",
            "output": report
        })
        print("  ✓ Report generated")
        print()

        return {
            "analysis": analysis,
            "report": report
        }

    def _generate_report(self, analysis: dict) -> str:
        """
        Generate human-readable triage report.

        Format matches Listing 2.12 from the chapter.

        Args:
            analysis: Output from TriageAnalyzerTool

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("NMAP TRIAGE REPORT")
        lines.append("=" * 70)
        lines.append("")

        # High priority findings
        if analysis["high_priority"]:
            lines.append("HIGH-INTEREST FINDINGS:")
            lines.append("")
            for idx, host in enumerate(analysis["high_priority"], 1):
                lines.append(f"{idx}. {host['hostname']}")

                # List findings
                for finding in host["findings"]:
                    if finding["severity"] == "high":
                        if finding["type"] == "legacy_service":
                            lines.append(f"   - {finding['service'].upper()} ({finding['port']}/tcp) exposed publicly")
                        elif finding["type"] == "eol_software":
                            lines.append(f"   - {finding['version']} (end-of-life)")

                # Add reason
                reasons = [f["reason"] for f in host["findings"] if f["severity"] == "high"]
                if reasons:
                    lines.append(f"   Reason: {reasons[0]}")
                lines.append("")

        # Medium priority findings
        if analysis["medium_priority"]:
            lines.append("MEDIUM-INTEREST FINDINGS:")
            lines.append("")
            for idx, host in enumerate(analysis["medium_priority"], 1):
                lines.append(f"{idx}. {host['hostname']}")

                # List findings
                for finding in host["findings"]:
                    if finding["type"] == "non_standard_port":
                        lines.append(f"   - {finding['service'].upper()} service on {finding['port']}/tcp")
                    elif finding["type"] == "odd_combination":
                        lines.append(f"   - {finding['reason']}")

                lines.append("")

        # Low priority findings
        if analysis["low_priority"]:
            lines.append("LOWER-INTEREST FINDINGS:")
            lines.append("")
            for host in analysis["low_priority"]:
                services = ", ".join([
                    f"{s['service']}({s['port']}/tcp)"
                    for s in host["services"][:3]  # Show first 3
                ])
                lines.append(f"- {host['hostname']}")
                lines.append(f"  - {services}")
                lines.append(f"  Reason: Common service combination with no immediate anomalies")
                lines.append("")

        lines.append("=" * 70)
        lines.append(f"Summary: {analysis['summary']['total_hosts']} hosts analyzed")
        lines.append(f"  High priority: {analysis['summary']['high_count']}")
        lines.append(f"  Medium priority: {analysis['summary']['medium_count']}")
        lines.append(f"  Low priority: {analysis['summary']['low_count']}")
        lines.append("=" * 70)

        return "\n".join(lines)


def main():
    """Run NMAP triage agent demonstration."""
    print("=" * 70)
    print("Example 8: NMAP Triage Agent")
    print("=" * 70)
    print()
    print("This example demonstrates:")
    print("- Offline analysis of saved nmap output (no live scanning)")
    print("- Risk-based prioritization of targets")
    print("- Actionable triage reports for bug hunters")
    print("- Complete audit logging")
    print()

    # Load sample nmap output
    data_file = Path(__file__).parent.parent / "data" / "nmap_output.txt"

    if not data_file.exists():
        print(f"ERROR: Sample data file not found: {data_file}")
        return 1

    with open(data_file, "r") as f:
        nmap_output = f.read()

    print(f"Loaded nmap output from: {data_file.name}")
    print()

    # Create logger and agent
    logger = ArtifactLogger()
    agent = NmapTriageAgent(logger)

    # Run triage
    result = agent.run(nmap_output)

    # Display report
    print(result["report"])
    print()

    print("=" * 70)
    print("✓ Triage complete")
    print()
    print("Key Takeaways:")
    print("- Agent never touched the network (offline analysis only)")
    print("- Flagged legacy services (telnet, old Apache)")
    print("- Identified non-standard ports (8443)")
    print("- Spotted odd combinations (FTP + web server)")
    print("- All decisions logged to runs/ directory")
    print()
    print("This workflow scales: same logic works on 10 hosts or 10,000 hosts.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
