#!/usr/bin/env python3
"""
Artifact logging demonstration.

From Listing 2.9 in Black Hat AI.

Demonstrates:
- Creating structured audit logs
- Recording agent actions with metadata
- JSONL format for analysis
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.logger import ArtifactLogger


def main():
    """Run artifact logging demonstration."""
    print("=" * 60)
    print("Example 5: Artifact Logging")
    print("=" * 60)
    print()

    # Initialize logger
    logger = ArtifactLogger(run_dir="runs")
    print(f"Initialized logger with run ID: {logger.run_id}")
    print(f"Log file: {logger.path}")
    print()

    # Simulate a single agent action and log it
    print("Simulating agent reconnaissance phase...")
    print("-" * 60)

    record = {
        "run_id": logger.run_id,
        "agent": "triage",
        "stage": "recon",
        "input": "Check reachability of example.com",
        "output": "example.com is reachable.",
        "approved_by": "operator@example.com",
        "status": "success",
    }
    logger.write(record)
    print("✓ Logged: recon action (timestamp injected by logger)")

    logger.close()

    print()
    print("=" * 60)
    print("Example completed.")
    print()
    print(f"View logs with: cat {logger.path} | jq")
    print()
    print("Benefits:")
    print("- Complete audit trail for compliance")
    print("- JSONL format for streaming analysis")
    print("- Structured data for ML/analytics")
    print("- Per-run isolation with UUID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
