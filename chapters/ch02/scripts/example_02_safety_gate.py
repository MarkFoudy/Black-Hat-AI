#!/usr/bin/env python3
"""
Safety gate demonstration.

From Listing 2.10 in Black Hat AI.

Demonstrates:
- Using safety gates for human-in-the-loop control
- Prohibited host filtering
- User confirmation workflow
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from src.safety.gates import safety_gate, simple_gate
from src.tools.ping import ping_host

# Load environment variables
load_dotenv()


def main():
    """Run safety gate demonstration."""
    print("=" * 60)
    print("Example 2: Safety Gates")
    print("=" * 60)
    print()

    # Test targets (mix of safe and prohibited)
    targets = [
        "example.com",
        "test.example.com",
        "prod-db-01.example.com",  # Should be blocked
        "payment-gateway.example.com",  # Should be blocked
    ]

    print("Testing safety gate with prohibited host filtering...")
    print("Prohibited hosts: prod, payment, core-db")
    print()

    for host in targets:
        print(f"{'='*60}")
        print(f"Target: {host}")
        print(f"{'='*60}")

        # Use safety gate
        if safety_gate("ping", {"target": host}):
            print(f"[Action] Pinging {host}...")
            result = ping_host(host)
            print(f"[Result] Reachable: {result['reachable']}")
        else:
            print(f"[Action] Skipped (denied by safety gate)")

        print()

    # Demonstrate simple gate
    print("\n" + "=" * 60)
    print("Testing simple gate (no automatic filtering)...")
    print("=" * 60)
    print()

    test_host = "192.168.1.1"
    if simple_gate("ping", {"target": test_host}):
        print(f"[Action] Pinging {test_host}...")
        result = ping_host(test_host)
        print(f"[Result] Reachable: {result['reachable']}")
    else:
        print("[Action] Skipped (denied by user)")

    print("\nExample completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
