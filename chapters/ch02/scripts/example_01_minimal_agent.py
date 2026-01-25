#!/usr/bin/env python3
"""
Minimal Agent Example

From Listing 2.7 in Black Hat AI Chapter 2.

Demonstrates:
- Pure Python agent implementation (no frameworks)
- Sequential tool execution
- Artifact logging
- Explicit decision-making

This example shows the smallest possible agent that still exhibits core
agent behaviors: orchestrating tools, recording actions, and producing
reproducible results.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.logger import ArtifactLogger
from src.core.agent import MinimalAgent
from src.tools.extract_urls import ExtractUrlsTool
from src.tools.summarize_urls import SummarizeUrlsTool


def main():
    """Run minimal agent demonstration."""
    print("=" * 60)
    print("Example 1: Minimal Agent")
    print("=" * 60)
    print()
    print("This example demonstrates a pure Python agent with:")
    print("- No AI frameworks (no LangChain, AutoGen, etc.)")
    print("- No LLM calls (all logic is explicit)")
    print("- Two simple tools: URL extraction and summarization")
    print("- Complete artifact logging for auditability")
    print()

    # Create logger
    logger = ArtifactLogger()
    print(f"✓ Artifact logger initialized (writing to runs/)")
    print()

    # Create agent with two tools
    agent = MinimalAgent(
        tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
        logger=logger
    )
    print("✓ MinimalAgent created with 2 tools:")
    print("  - extract_urls: Extract URLs from text")
    print("  - summarize_urls: Count and summarize URLs")
    print()

    # Run agent
    test_input = "Check https://example.com and https://admin.example.com/login"
    print("Input:")
    print(f"  \"{test_input}\"")
    print()

    print("Running agent workflow...")
    print()

    result = agent.run(test_input)

    print("Result:")
    print(f"  URLs found: {result['count']}")
    print(f"  Summary: {result['summary']}")
    print()

    print("=" * 60)
    print("✓ Agent execution complete")
    print()
    print("Key Concepts Demonstrated:")
    print("- Explicit control flow (no hidden framework logic)")
    print("- Tool orchestration (extract → summarize)")
    print("- Artifact logging (every step recorded)")
    print("- No external dependencies (pure Python + regex)")
    print()
    print("Check the runs/ directory for artifact logs")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
