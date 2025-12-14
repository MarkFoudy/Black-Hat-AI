#!/usr/bin/env python3
"""
AutoGen multi-agent example.

From Listing 2.11 in Black Hat AI.

Demonstrates:
- Creating AutoGen agents (Assistant + UserProxy)
- Multi-agent conversation
- Tool registration (conceptual)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run AutoGen agent example."""
    print("=" * 60)
    print("Example 3: AutoGen Multi-Agent System")
    print("=" * 60)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        print("Please copy .env.example to .env and configure your API key")
        return 1

    try:
        from src.adapters.autogen.agent import build_autogen_agent
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Install AutoGen with: pip install pyautogen")
        return 1

    # Build AutoGen agent
    try:
        print("Building AutoGen agent system...")
        agent_run = build_autogen_agent()
    except Exception as e:
        print(f"ERROR: Failed to build agent: {e}")
        return 1

    # Run example task
    task = "Check reachability of example.com"
    print(f"\nTask: {task}")
    print("=" * 60)

    try:
        result = agent_run(task)
        print(f"\nResult: {result}")
    except Exception as e:
        print(f"ERROR: Agent failed: {e}")
        return 1

    print("\nExample completed. Check the 'runs/' directory for logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
