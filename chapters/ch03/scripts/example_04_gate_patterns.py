#!/usr/bin/env python3
"""
Example 4: Safety Gate Patterns

From Listings 3.5, 3.6 and Table 3.4 in Black Hat AI.

Demonstrates all gate types:
- GlobalGate: Time-based restrictions
- ScopeGate: Authorized target filtering
- TimeWindowGate: Business hours enforcement
- ApprovalGate: Human-in-the-loop confirmation
- EnvironmentGate: Production system blocking

Run:
    python scripts/example_04_gate_patterns.py
"""

import sys
import os
from datetime import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.gates import (
    GlobalGate,
    ScopeGate,
    TimeWindowGate,
    ApprovalGate,
    EnvironmentGate,
)
from src.agents import ReconAgent


def main():
    """Demonstrate all gate patterns."""
    print("=" * 60)
    print("Example 4: Safety Gate Patterns")
    print("=" * 60)
    print()

    # Create a sample stage for testing
    class MockStage:
        def __init__(self, name, target=None):
            self.name = name
            self.target = target
            self.targets = [target] if target else []

    # 1. GlobalGate (Listing 3.6)
    print("1. GlobalGate - Time-based restrictions")
    print("-" * 40)
    gate1 = GlobalGate(start_hour=7, end_hour=22)
    print(f"   Config: {gate1}")

    stage = MockStage("test_stage")
    result = gate1.allow(stage)
    print(f"   Allow test_stage now? {result}")
    print()

    # 2. ScopeGate
    print("2. ScopeGate - Authorized target filtering")
    print("-" * 40)
    gate2 = ScopeGate(
        authorized_domains=["example.com"],
        excluded_patterns=["prod", "payment"],
    )
    print(f"   Config: {gate2}")

    # Test with different targets
    for target in ["api.example.com", "api.other.com", "prod.example.com"]:
        stage = MockStage("scan", target=target)
        result = gate2.allow(stage)
        print(f"   Allow scan on {target}? {result}")
    print()

    # 3. TimeWindowGate
    print("3. TimeWindowGate - Business hours enforcement")
    print("-" * 40)
    gate3 = TimeWindowGate(
        start_time=time(9, 0),
        end_time=time(17, 0),
        allowed_days=[0, 1, 2, 3, 4],  # Mon-Fri
    )
    print(f"   Config: {gate3}")

    stage = MockStage("scan")
    result = gate3.allow(stage)
    print(f"   Allow scan now (business hours check)? {result}")
    print()

    # 4. ApprovalGate
    print("4. ApprovalGate - Human-in-the-loop confirmation")
    print("-" * 40)
    gate4 = ApprovalGate(
        require_approval_for=["exploit", "exfil"],
        auto_approve=True,  # Auto-approve for demo
    )
    print(f"   Config: {gate4}")

    for stage_name in ["recon", "exploit", "report"]:
        stage = MockStage(stage_name)
        result = gate4.allow(stage)
        print(f"   Allow {stage_name}? {result}")
    print()

    # 5. EnvironmentGate (Listing 3.5)
    print("5. EnvironmentGate - Production system blocking")
    print("-" * 40)
    gate5 = EnvironmentGate(
        prohibited_patterns=["prod", "payment", "core-db"],
        check_hostname=False,  # Don't check local hostname for demo
    )
    print(f"   Config: {gate5}")

    for target in ["staging.example.com", "prod.example.com", "payment.example.com"]:
        stage = MockStage("scan", target=target)
        result = gate5.allow(stage)
        print(f"   Allow scan on {target}? {result}")
    print()

    # Demonstrate gate composition
    print("=" * 60)
    print("Gate Composition - Multiple gates in sequence")
    print("=" * 60)
    print()

    all_gates = [
        GlobalGate(start_hour=0, end_hour=23),  # Always allow for demo
        ScopeGate(authorized_domains=["example.com"]),
        EnvironmentGate(prohibited_patterns=["prod"], check_hostname=False),
    ]

    targets = ["api.example.com", "prod.example.com", "api.other.com"]

    for target in targets:
        stage = MockStage("scan", target=target)
        results = [(type(g).__name__, g.allow(stage)) for g in all_gates]

        all_pass = all(r[1] for r in results)
        print(f"Target: {target}")
        for gate_name, passed in results:
            status = "PASS" if passed else "BLOCK"
            print(f"  {gate_name}: {status}")
        print(f"  Final: {'ALLOWED' if all_pass else 'BLOCKED'}")
        print()

    print("Key Takeaways:")
    print("- Gates provide declarative safety controls")
    print("- Multiple gates can be composed for layered security")
    print("- All gates must pass for a stage to execute")

    return 0


if __name__ == "__main__":
    sys.exit(main())
