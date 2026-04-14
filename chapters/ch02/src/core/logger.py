"""
Artifact logging for AI agent runs.

From Listing 2.5 in Black Hat AI.

This module provides persistent logging of agent interactions to JSONL files.
Each agent run creates a unique log file for audit, debugging, and analysis.
"""

import json
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any


class ArtifactLogger:
    """
    Logs agent artifacts to JSONL files for audit and analysis.

    Each logger instance creates a unique file identified by UUID.
    Logs are written in JSON Lines format (one JSON object per line)
    for easy streaming and analysis.

    Example:
        with ArtifactLogger() as logger:
            logger.write({"action": "scan", "target": "example.com"})
        # Logs written to runs/<uuid>.jsonl

    Note:
        Files are flushed after each write to ensure data persistence
        even if the process crashes.
    """

    def __init__(self, run_dir: str = "runs") -> None:
        """
        Initialize the artifact logger.

        Args:
            run_dir: Directory to store log files (created if doesn't exist)
        """
        os.makedirs(run_dir, exist_ok=True)
        self.run_id = str(uuid.uuid4())
        self._file = open(
            f"{run_dir}/{self.run_id}.jsonl", "w", encoding="utf8"
        )

    def write(self, record: Dict[str, Any]) -> None:
        """
        Write a record to the log file.

        If the record does not contain a "timestamp" key, one is injected
        automatically using the current UTC time.

        Args:
            record: Dictionary to log (will be serialized to JSON)
        """
        if "timestamp" not in record:
            record["timestamp"] = datetime.now(timezone.utc).isoformat()
        json.dump(record, self._file)
        self._file.write("\n")
        self._file.flush()

    def close(self) -> None:
        """Close the log file."""
        if self._file and not self._file.closed:
            self._file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed."""
        self.close()
