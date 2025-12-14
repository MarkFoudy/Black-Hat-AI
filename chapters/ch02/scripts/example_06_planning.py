#!/usr/bin/env python3
"""
Planning and reasoning demonstration.

From Listing 2.17 in Black Hat AI.

Demonstrates:
- Using agents for prioritization and triage
- Reasoning about targets without direct action
- Strategic planning phase
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from data.targets import targets

# Load environment variables
load_dotenv()


def main():
    """Run planning/reasoning demonstration."""
    print("=" * 60)
    print("Example 6: Planning & Reasoning")
    print("=" * 60)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        print("Please copy .env.example to .env and configure your API key")
        return 1

    try:
        from src.adapters.selector import get_agent
    except ImportError as e:
        print(f"ERROR: {e}")
        return 1

    # Prepare triage prompt
    input_text = (
        "Given these host entries, rank which are most likely "
        "to expose sensitive admin or test interfaces. "
        "Explain your reasoning briefly."
    )

    print("Targets to analyze:")
    print("-" * 60)
    for target in targets:
        print(f"  - {target}")
    print()

    # Create triage agent (no tools - pure reasoning)
    try:
        print("Creating triage agent...")
        triage_agent = get_agent(adapter="langchain", tools=[])
    except Exception as e:
        print(f"ERROR: Failed to create agent: {e}")
        return 1

    # Run triage analysis
    print("\nAnalyzing targets...")
    print("=" * 60)

    try:
        result = triage_agent(f"{input_text}\n\nTargets:\n" + "\n".join(targets))
        print("\nTriage Analysis:")
        print("-" * 60)
        print(result)
    except Exception as e:
        print(f"ERROR: Agent failed: {e}")
        return 1

    print()
    print("=" * 60)
    print("Example completed.")
    print()
    print("Key Concepts:")
    print("- Agents can reason without taking actions")
    print("- Useful for planning and prioritization phases")
    print("- Reduces risks by separating thinking from acting")
    print("- Foundation for multi-stage attack workflows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
