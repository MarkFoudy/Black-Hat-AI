#!/usr/bin/env python3
"""
Example 5: Resilience Patterns

From Listings 3.8, 3.9, and 3.10 in Black Hat AI.

Demonstrates error handling and recovery:
- Retry with exponential backoff
- Checkpointing for resumable runs
- Alert hooks for monitoring

Run:
    python scripts/example_05_resilience.py
"""

import sys
import os
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.artifact import PipelineArtifact
from src.resilience import retry_stage, Checkpoint, safe_run, AlertHandler, send_alert


def main():
    """Demonstrate resilience patterns."""
    print("=" * 60)
    print("Example 5: Resilience Patterns")
    print("=" * 60)
    print()

    # 1. Retry with Exponential Backoff (Listing 3.8)
    print("1. Retry with Exponential Backoff")
    print("-" * 40)

    class FlakyStage:
        """A stage that fails randomly to demonstrate retry."""
        name = "flaky_stage"
        fail_count = 0
        max_failures = 2  # Succeed on 3rd try

        def run(self, artifact):
            self.fail_count += 1
            if self.fail_count <= self.max_failures:
                raise ConnectionError(f"Simulated failure #{self.fail_count}")
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={"result": "success after retries"},
                success=True,
            )

    flaky = FlakyStage()
    print(f"   Running flaky stage (will fail {flaky.max_failures} times)...")

    try:
        # Use shorter delays for demo
        result = retry_stage(flaky, None, retries=3, base_delay=0.5)
        print(f"   Final result: {result.output}")
    except RuntimeError as e:
        print(f"   All retries exhausted: {e}")

    print()

    # 2. Checkpointing (Listing 3.9)
    print("2. Checkpointing for Resumable Runs")
    print("-" * 40)

    class SimpleStage:
        def __init__(self, name):
            self.name = name

        def run(self, artifact):
            print(f"   Executing {self.name}...")
            return PipelineArtifact.from_previous(
                previous=artifact,
                stage=self.name,
                output={f"{self.name}_data": f"result from {self.name}"},
                success=True,
            )

    # Create checkpoint manager
    checkpoint = Checkpoint(run_dir="runs/checkpoints")
    print(f"   Checkpoint dir: runs/checkpoints/{checkpoint.run_id[:8]}...")

    stages = [SimpleStage("stage_a"), SimpleStage("stage_b"), SimpleStage("stage_c")]
    artifact = None

    # First run - executes all stages
    print("\n   First run (executing all stages):")
    for stage in stages:
        artifact = safe_run(stage, artifact, checkpoint)

    # Simulate resume (stages are already checkpointed)
    print("\n   Second run (loading from checkpoints):")
    checkpoint2 = Checkpoint(run_dir="runs/checkpoints", run_id=checkpoint.run_id)
    artifact = None
    for stage in stages:
        artifact = safe_run(stage, artifact, checkpoint2)

    print()

    # 3. Alert Hooks (Listing 3.10)
    print("3. Alert Hooks for Monitoring")
    print("-" * 40)

    handler = AlertHandler()

    # Simulate errors
    for i in range(6):
        try:
            raise ValueError(f"Simulated error #{i+1}")
        except Exception as e:
            handler.record_error("problematic_stage", e)

    print(f"   Total errors recorded: {handler.get_error_count()}")
    print(f"   Alerts triggered: {len(handler.alert_history)}")
    print()

    # Simple alert function (Listing 3.10 pattern)
    print("   Using simple send_alert():")
    error_count = 7
    run_id = "abc123"
    if error_count > 5:
        send_alert(f"Pipeline {run_id} failing repeatedly")

    print()
    print("Key Takeaways:")
    print("- Retry with backoff handles transient failures gracefully")
    print("- Checkpointing enables resume without re-running completed stages")
    print("- Alert hooks provide visibility into pipeline health")

    return 0


if __name__ == "__main__":
    sys.exit(main())
