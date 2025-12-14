#!/usr/bin/env python3
"""
Artifact logging demonstration.

From Listing 2.15 in Black Hat AI.

Demonstrates:
- Creating structured audit logs
- Recording agent actions with metadata
- JSONL format for analysis
"""

import sys
import os
from datetime import datetime

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
    print(f"Log file: runs/{logger.run_id}.jsonl")
    print()

    # Simulate agent actions and log them
    print("Simulating agent reconnaissance phase...")
    print("-" * 60)

    # Action 1: Initial scan
    record1 = {
        "run_id": logger.run_id,
        "agent": "triage",
        "stage": "recon",
        "timestamp": datetime.now().isoformat(),
        "input": "Check reachability of example.com",
        "output": "example.com is reachable.",
        "approved_by": "operator@example.com",
        "status": "success",
    }
    logger.write(record1)
    print("✓ Logged: Ping example.com (success)")

    # Action 2: Port scan
    record2 = {
        "run_id": logger.run_id,
        "agent": "scanner",
        "stage": "discovery",
        "timestamp": datetime.now().isoformat(),
        "input": "Scan ports 80,443 on example.com",
        "output": {"80": "open", "443": "open"},
        "approved_by": "operator@example.com",
        "status": "success",
    }
    logger.write(record2)
    print("✓ Logged: Port scan (success)")

    # Action 3: Failed attempt
    record3 = {
        "run_id": logger.run_id,
        "agent": "exploit",
        "stage": "attack",
        "timestamp": datetime.now().isoformat(),
        "input": "Attempt SQLi on login form",
        "output": None,
        "error": "WAF detected and blocked request",
        "approved_by": "operator@example.com",
        "status": "blocked",
    }
    logger.write(record3)
    print("✓ Logged: SQLi attempt (blocked)")

    # Close logger
    logger.close()

    print()
    print("=" * 60)
    print("Example completed.")
    print()
    print(f"View logs with: cat runs/{logger.run_id}.jsonl | jq")
    print(f"Or: tail -f runs/{logger.run_id}.jsonl")
    print()
    print("Benefits:")
    print("- Complete audit trail for compliance")
    print("- JSONL format for streaming analysis")
    print("- Structured data for ML/analytics")
    print("- Per-run isolation with UUID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
