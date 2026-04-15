#!/usr/bin/env python3
"""
Safety gate demonstration.

Shows the three-outcome behavior of safety_gate from Listing 2.8:
  1. Blocked  — target is in the prohibited set (no prompt shown)
  2. Approved — operator types 'y' at the confirmation prompt
  3. Denied   — operator types 'n' at the confirmation prompt

Run from the ch02 directory:
    python scripts/example_safety_gate.py

No network access is performed; this demo only calls safety_gate.
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.safety.gates import safety_gate


def demo_blocked():
    """Demonstrate automatic blocking of a prohibited target."""
    print("--- Outcome 1: Blocked (prohibited target) ---")
    result = safety_gate("scan", {"target": "prod.example.com"})
    print(f"Gate returned: {result}\n")


def demo_approved():
    """Demonstrate approval when the operator confirms."""
    print("--- Outcome 2: Approved ---")
    with patch("builtins.input", return_value="y"):
        result = safety_gate("scan", {"target": "staging.example.com"})
    print(f"Gate returned: {result}\n")


def demo_denied():
    """Demonstrate denial when the operator declines."""
    print("--- Outcome 3: Denied ---")
    with patch("builtins.input", return_value="n"):
        result = safety_gate("scan", {"target": "staging.example.com"})
    print(f"Gate returned: {result}\n")


if __name__ == "__main__":
    demo_blocked()
    demo_approved()
    demo_denied()
