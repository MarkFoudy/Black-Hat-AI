"""
Artifact logging for AI agent runs.

Duplicated from Chapter 2 with enhancements for multi-agent pipelines.

This module provides persistent logging of agent interactions to JSONL files.
Each agent run creates a unique log file for audit, debugging, and analysis.
"""

import json
import uuid
import os
from typing import Dict, Any, Optional, Union
from datetime import datetime

from .artifact import PipelineArtifact


class ArtifactLogger:
    """
    Logs agent artifacts to JSONL files for audit and analysis.

    Each logger instance creates a unique file identified by UUID.
    Logs are written in JSON Lines format (one JSON object per line)
    for easy streaming and analysis.

    Attributes:
        run_dir: Directory where log files are stored
        run_id: Unique identifier for this run
        file: Open file handle for writing logs

    Example:
        logger = ArtifactLogger(run_dir="runs")
        logger.write({"action": "ping", "target": "example.com", "result": "success"})
        logger.write_artifact(artifact)

    Note:
        Files are flushed after each write to ensure data persistence
        even if the process crashes.
    """

    def __init__(self, run_dir: str = "runs", run_id: Optional[str] = None) -> None:
        """
        Initialize the artifact logger.

        Args:
            run_dir: Directory to store log files (created if doesn't exist)
            run_id: Optional run ID to use (generates UUID if not provided)
        """
        os.makedirs(run_dir, exist_ok=True)
        self.run_dir = run_dir
        self.run_id = run_id or uuid.uuid4().hex
        self.file_path = f"{run_dir}/{self.run_id}.jsonl"
        self.file = open(self.file_path, "a", encoding="utf8")

    def write(self, record: Dict[str, Any]) -> None:
        """
        Write a record to the log file.

        Args:
            record: Dictionary to log (will be serialized to JSON)

        Note:
            The file is flushed after each write to ensure persistence.
        """
        # Ensure timestamp is serializable
        if "timestamp" in record and isinstance(record["timestamp"], datetime):
            record = record.copy()
            record["timestamp"] = record["timestamp"].isoformat()

        json.dump(record, self.file)
        self.file.write("\n")
        self.file.flush()

    def write_artifact(self, artifact: PipelineArtifact) -> None:
        """
        Write a PipelineArtifact to the log file.

        Args:
            artifact: The artifact to log
        """
        self.write(artifact.to_jsonl_record())

    def write_stage(
        self,
        stage: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        error: Optional[str] = None,
    ) -> PipelineArtifact:
        """
        Create and log a stage artifact in one call.

        Args:
            stage: Name of the stage
            input_data: Input to the stage
            output_data: Output from the stage
            success: Whether the stage succeeded
            error: Optional error message

        Returns:
            The created PipelineArtifact
        """
        artifact = PipelineArtifact(
            run_id=self.run_id,
            stage=stage,
            input=input_data,
            output=output_data,
            success=success,
            error=error,
        )
        self.write_artifact(artifact)
        return artifact

    def close(self) -> None:
        """Close the log file."""
        if self.file and not self.file.closed:
            self.file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed."""
        self.close()


def load_artifacts(run_dir: str, run_id: str) -> list[PipelineArtifact]:
    """
    Load all artifacts from a run.

    Args:
        run_dir: Directory containing run files
        run_id: The run ID to load

    Returns:
        List of PipelineArtifact objects from the run
    """
    file_path = f"{run_dir}/{run_id}.jsonl"
    artifacts = []

    if not os.path.exists(file_path):
        return artifacts

    with open(file_path, "r", encoding="utf8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                # Convert ISO timestamp back to datetime
                if "timestamp" in data and isinstance(data["timestamp"], str):
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                artifacts.append(PipelineArtifact(**data))

    return artifacts
