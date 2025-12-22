#!/usr/bin/env python3
"""
Example: Scope-Gated Reconnaissance (Section 4.6)

Demonstrates:
1. Loading scope configuration from JSON
2. Running the pipeline with scope enforcement
3. Showing blocked hosts logged as scope-v1 artifacts
4. Using time-window gating

This example shows how to build responsible reconnaissance
systems that operate within authorized boundaries.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.artifacts import Artifact, ScopeArtifact, write_jsonl, read_jsonl
from src.recon.pipeline import PipelineConfig, ReconPipeline
from src.recon.dns import candidates
from src.safety.scope import ScopeConfig, ScopeChecker, save_scope
from src.safety.gates import time_window_gate, approval_gate, GateChain


def example_basic_scope():
    """Demonstrate basic scope checking."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Scope Checking")
    print("=" * 60)

    # Create a scope configuration
    config = ScopeConfig(
        allowed=["example.com", "*.example.com"],
        forbidden=["prod.example.com", "*.prod.example.com"],
    )

    checker = ScopeChecker(config)

    # Test various hosts
    test_hosts = [
        "example.com",
        "www.example.com",
        "api.example.com",
        "dev.example.com",
        "prod.example.com",
        "api.prod.example.com",
        "other-domain.com",
    ]

    print("\nScope configuration:")
    print(f"  Allowed: {config.allowed}")
    print(f"  Forbidden: {config.forbidden}")
    print("\nChecking hosts:")

    for host in test_hosts:
        allowed, reason = checker.is_allowed(host)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  {host:<30} {status:<10} ({reason})")


def example_scoped_pipeline():
    """Demonstrate pipeline with scope enforcement."""
    print("\n" + "=" * 60)
    print("Example 2: Scoped Pipeline Execution")
    print("=" * 60)

    # Create scope - allow test domains, forbid prod
    config = ScopeConfig(
        allowed=["example.com", "*.example.com"],
        forbidden=["prod.*", "*.prod.*"],
    )
    checker = ScopeChecker(config)

    # Generate candidates
    root = "example.com"
    hosts = [root] + candidates(root)

    print(f"\nTarget: {root}")
    print(f"Candidates: {hosts}")

    # Filter by scope
    allowed_hosts, blocked_hosts = checker.filter_hosts(hosts)

    print(f"\nAllowed hosts ({len(allowed_hosts)}):")
    for h in allowed_hosts:
        print(f"  - {h}")

    print(f"\nBlocked hosts ({len(blocked_hosts)}):")
    for h in blocked_hosts:
        print(f"  - {h}")

    # Create scope-checking function for pipeline
    def scope_check(host: str) -> bool:
        allowed, reason = checker.is_allowed(host)
        if not allowed:
            print(f"  [SCOPE] Blocked: {host} ({reason})")
        return allowed

    # Run pipeline in dry-run mode
    pipeline_config = PipelineConfig(
        dry_run=True,
        verbose=True,
    )
    pipeline = ReconPipeline(pipeline_config, scope_checker=scope_check)

    print("\nRunning pipeline (dry-run):")
    result = pipeline.run(root)
    print(f"\nWould scan {result.hosts_scanned} hosts")


def example_gate_chain():
    """Demonstrate chained safety gates."""
    print("\n" + "=" * 60)
    print("Example 3: Gate Chain")
    print("=" * 60)

    # Create scope checker
    scope_config = ScopeConfig(
        allowed=["example.com", "*.example.com"],
        forbidden=[],
    )
    checker = ScopeChecker(scope_config)

    host = "api.example.com"

    print(f"\nChecking gates for host: {host}")

    # Build gate chain
    chain = GateChain()
    chain.add(lambda: time_window_gate(0, 24))  # Always pass (0-24 hours)
    chain.add(lambda: checker.is_allowed(host))

    # Run gates
    all_passed = chain.check_and_report(verbose=True)

    print(f"\nAll gates passed: {all_passed}")


def example_scope_artifacts():
    """Demonstrate logging scope decisions as artifacts."""
    print("\n" + "=" * 60)
    print("Example 4: Scope Decision Artifacts")
    print("=" * 60)

    output_file = "runs/scope_example.jsonl"

    # Remove old file if exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Create scope checker
    config = ScopeConfig(
        allowed=["example.com", "*.example.com"],
        forbidden=["prod.example.com"],
    )
    checker = ScopeChecker(config)

    # Check hosts and log decisions
    test_hosts = [
        "example.com",
        "api.example.com",
        "prod.example.com",
    ]

    print(f"\nLogging scope decisions to: {output_file}")

    for host in test_hosts:
        allowed = checker.check_and_log(host, output_file)
        status = "allowed" if allowed else "blocked"
        print(f"  {host}: {status}")

    # Read back and display
    print("\nRecorded artifacts:")
    for record in read_jsonl(output_file):
        print(f"  {record}")


def example_save_load_scope():
    """Demonstrate saving and loading scope configuration."""
    print("\n" + "=" * 60)
    print("Example 5: Save/Load Scope Configuration")
    print("=" * 60)

    scope_file = "data/scope.json"

    # Create and save scope
    config = ScopeConfig(
        allowed=["example.com", "*.example.com", "test.local"],
        forbidden=["prod.*", "*.gov", "payments.*"],
    )

    print(f"\nSaving scope to: {scope_file}")
    save_scope(config, scope_file)

    # Display the file contents
    with open(scope_file, "r") as f:
        print(f"\nFile contents:\n{f.read()}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Chapter 4: Scope and Safety Gates Examples")
    print("=" * 60)

    example_basic_scope()
    example_scoped_pipeline()
    example_gate_chain()
    example_scope_artifacts()
    example_save_load_scope()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
