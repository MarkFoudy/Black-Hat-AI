#!/usr/bin/env python3
"""
Basic agent execution with LangChain.

From Listing 2.8 in Black Hat AI.

Demonstrates:
- Creating a LangChain agent with tools
- Running simple reconnaissance tasks
- Handling both successful and failed operations
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from src.adapters.langchain.agent import build_langchain_agent
from src.adapters.langchain.tools import ping_host_tool

# Load environment variables
load_dotenv()


def main():
    """Run basic agent execution example."""
    print("=" * 60)
    print("Example 1: Basic Agent Execution")
    print("=" * 60)
    print()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        print("Please copy .env.example to .env and configure your API key")
        return 1

    # Build agent with ping tool
    try:
        if ping_host_tool is None:
            print("ERROR: LangChain not installed")
            print("Install with: pip install langchain langchain-openai")
            return 1

        print("Building LangChain agent with ping tool...")
        agent_run = build_langchain_agent([ping_host_tool])
    except Exception as e:
        print(f"ERROR: Failed to build agent: {e}")
        return 1

    # Test targets
    targets = ["example.com", "no-such-host.local"]

    print(f"Testing {len(targets)} targets...")
    print()

    # Run agent on each target
    for host in targets:
        print(f"{'='*60}")
        print(f"Target: {host}")
        print(f"{'='*60}")

        try:
            result = agent_run(f"Check reachability of {host}")
            print(f"Result: {result}")
        except Exception as e:
            print(f"ERROR: Agent failed: {e}")

        print()

    print("Example completed. Check the 'runs/' directory for logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
