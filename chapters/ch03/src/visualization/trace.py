"""
Trace summarization for pipeline runs.

From Listing 3.4 in Black Hat AI.

Provides functions to summarize and visualize pipeline execution traces.
"""

import json
import glob as glob_module
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


def summarize_run(run_dir: str) -> None:
    """
    Print a summary of all stages in a pipeline run.

    From Listing 3.4 in Black Hat AI.

    Reads all JSONL files in the run directory and prints a formatted
    trace showing timestamp, stage, and success status for each event.

    Args:
        run_dir: Directory containing run artifacts (*.jsonl files)

    Example:
        summarize_run("runs/74bfe8c0f5c84c16b7d90a2c334c9e0b")

        # Output:
        # 2025-03-01 10:03 | recon   | success=True
        # 2025-03-01 10:04 | triage  | success=True
        # 2025-03-01 10:05 | report  | success=True
    """
    print(f"\n{'='*60}")
    print(f"Pipeline Trace: {os.path.basename(run_dir)}")
    print(f"{'='*60}")

    # Find all JSONL files in the directory
    pattern = os.path.join(run_dir, "*.jsonl")
    files = sorted(glob_module.glob(pattern))

    if not files:
        print(f"No artifacts found in {run_dir}")
        return

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    rec = json.loads(line)
                    timestamp = rec.get("timestamp", "unknown")
                    stage = rec.get("stage", "unknown")
                    success = rec.get("success", "?")

                    # Format timestamp if it's an ISO string
                    if isinstance(timestamp, str) and "T" in timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass

                    print(f"{timestamp} | {stage:12} | success={success}")

                except json.JSONDecodeError:
                    continue

    print(f"{'='*60}\n")


def format_trace(artifacts: List[Dict[str, Any]]) -> str:
    """
    Format a list of artifacts as a trace string.

    Args:
        artifacts: List of artifact dictionaries

    Returns:
        Formatted trace string
    """
    lines = []
    lines.append(f"{'Timestamp':<20} | {'Stage':<12} | {'Status':<10}")
    lines.append("-" * 50)

    for artifact in artifacts:
        timestamp = artifact.get("timestamp", "unknown")
        stage = artifact.get("stage", "unknown")
        success = artifact.get("success", False)
        status = "SUCCESS" if success else "FAILED"

        # Format timestamp
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(timestamp, str) and "T" in timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        lines.append(f"{timestamp:<20} | {stage:<12} | {status:<10}")

    return "\n".join(lines)


def get_run_summary(run_dir: str) -> Dict[str, Any]:
    """
    Get a structured summary of a pipeline run.

    Args:
        run_dir: Directory containing run artifacts

    Returns:
        Dictionary with run summary information
    """
    pattern = os.path.join(run_dir, "*.jsonl")
    files = sorted(glob_module.glob(pattern))

    stages = []
    total_success = 0
    total_failed = 0
    start_time = None
    end_time = None

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    rec = json.loads(line)
                    stage_name = rec.get("stage", "unknown")
                    success = rec.get("success", False)
                    timestamp = rec.get("timestamp", "")

                    # Parse timestamp
                    if isinstance(timestamp, str) and timestamp:
                        try:
                            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            if start_time is None or ts < start_time:
                                start_time = ts
                            if end_time is None or ts > end_time:
                                end_time = ts
                        except ValueError:
                            pass

                    stages.append({
                        "name": stage_name,
                        "success": success,
                        "timestamp": timestamp,
                    })

                    if success:
                        total_success += 1
                    else:
                        total_failed += 1

                except json.JSONDecodeError:
                    continue

    duration = None
    if start_time and end_time:
        duration = (end_time - start_time).total_seconds()

    return {
        "run_id": os.path.basename(run_dir),
        "stages": stages,
        "total_stages": len(stages),
        "successful": total_success,
        "failed": total_failed,
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None,
        "duration_seconds": duration,
    }


def list_runs(runs_dir: str = "runs") -> List[str]:
    """
    List all pipeline runs in a directory.

    Args:
        runs_dir: Directory containing run subdirectories

    Returns:
        List of run IDs
    """
    if not os.path.exists(runs_dir):
        return []

    runs = []
    for item in os.listdir(runs_dir):
        path = os.path.join(runs_dir, item)
        if os.path.isfile(path) and item.endswith(".jsonl"):
            # Run ID is the filename without extension
            runs.append(item[:-6])
        elif os.path.isdir(path):
            # Run ID is the directory name
            runs.append(item)

    return sorted(runs)
