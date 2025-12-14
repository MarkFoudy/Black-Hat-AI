#!/usr/bin/env python3
"""
Reflection and summary generation.

From Listing 2.18 in Black Hat AI.

Demonstrates:
- Using agents to reflect on completed work
- Generating summaries and reports
- Identifying gaps and next steps
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run reflection/summary demonstration."""
    print("=" * 60)
    print("Example 7: Reflection & Summary Generation")
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

    # Create triage agent
    try:
        print("Creating triage agent for reflection...")
        triage_agent = get_agent(adapter="langchain", tools=[])
    except Exception as e:
        print(f"ERROR: Failed to create agent: {e}")
        return 1

    # Reflection prompt
    summary_prompt = (
        "Summarize our findings from the triage phase. "
        "List top priorities and any gaps that require manual review. "
        "\n\nContext: We analyzed several targets including admin.example.com, "
        "test.example.com, and found that admin interfaces and production "
        "databases are the highest priority targets."
    )

    print("Generating reflection summary...")
    print("=" * 60)

    try:
        report = triage_agent(summary_prompt)
        print("\nReflection Report:")
        print("-" * 60)
        print(report)
    except Exception as e:
        print(f"ERROR: Agent failed: {e}")
        return 1

    print()
    print("=" * 60)
    print("Example completed.")
    print()
    print("Use Cases for Reflection:")
    print("- End-of-phase summaries")
    print("- Identifying overlooked attack vectors")
    print("- Generating human-readable reports")
    print("- Planning next stages of engagement")
    print("- Learning from successes and failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
