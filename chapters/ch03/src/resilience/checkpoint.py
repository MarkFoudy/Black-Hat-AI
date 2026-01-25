"""
Checkpointing for resumable pipeline runs.

From Listing 3.2 in Black Hat AI.

Enables pipelines to save progress and resume from the last successful stage.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.artifact import PipelineArtifact


class Checkpoint:
    """
    Manages checkpoint storage for pipeline stages.

    Checkpoints save the output of each stage so that pipelines can
    resume from the last successful point after a failure.

    Attributes:
        run_dir: Directory for storing checkpoint files
        run_id: Unique identifier for this run

    Example:
        checkpoint = Checkpoint("runs", "abc123")
        if checkpoint.exists("recon"):
            artifact = checkpoint.load("recon")
        else:
            artifact = recon_agent.run(None)
            checkpoint.save("recon", artifact)
    """

    def __init__(self, run_dir: str = "runs", run_id: Optional[str] = None):
        """
        Initialize checkpoint manager.

        Args:
            run_dir: Directory for checkpoint files
            run_id: Optional run ID (generates if not provided)
        """
        import uuid

        self.run_dir = run_dir
        self.run_id = run_id or uuid.uuid4().hex

        # Create run directory
        self.checkpoint_dir = os.path.join(run_dir, self.run_id)
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def _get_path(self, stage_name: str) -> str:
        """Get checkpoint file path for a stage."""
        return os.path.join(self.checkpoint_dir, f"{stage_name}.json")

    def exists(self, stage_name: str) -> bool:
        """Check if a checkpoint exists for a stage."""
        return os.path.exists(self._get_path(stage_name))

    def save(self, stage_name: str, artifact: PipelineArtifact) -> str:
        """
        Save a checkpoint for a stage.

        Args:
            stage_name: Name of the stage
            artifact: Artifact to checkpoint

        Returns:
            Path to the checkpoint file
        """
        path = self._get_path(stage_name)
        data = artifact.to_jsonl_record()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[Checkpoint] Saved '{stage_name}' to {path}")
        return path

    def load(self, stage_name: str) -> Optional[PipelineArtifact]:
        """
        Load a checkpoint for a stage.

        Args:
            stage_name: Name of the stage

        Returns:
            PipelineArtifact if checkpoint exists, None otherwise
        """
        path = self._get_path(stage_name)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert timestamp string back to datetime
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        print(f"[Checkpoint] Loaded '{stage_name}' from {path}")
        return PipelineArtifact(**data)

    def clear(self, stage_name: Optional[str] = None) -> None:
        """
        Clear checkpoints.

        Args:
            stage_name: Specific stage to clear (None = clear all)
        """
        if stage_name:
            path = self._get_path(stage_name)
            if os.path.exists(path):
                os.remove(path)
                print(f"[Checkpoint] Cleared '{stage_name}'")
        else:
            for file in os.listdir(self.checkpoint_dir):
                os.remove(os.path.join(self.checkpoint_dir, file))
            print(f"[Checkpoint] Cleared all checkpoints for run {self.run_id}")

    def list_stages(self) -> list[str]:
        """List all checkpointed stages."""
        stages = []
        for file in os.listdir(self.checkpoint_dir):
            if file.endswith(".json"):
                stages.append(file[:-5])  # Remove .json extension
        return stages


def safe_run(
    stage: Any,
    artifact: Optional[PipelineArtifact],
    checkpoint: Optional[Checkpoint] = None,
    run_dir: str = "runs",
) -> PipelineArtifact:
    """
    Execute a stage with automatic checkpointing.

    From Listing 3.9 in Black Hat AI.

    If a checkpoint exists for this stage, load and return it.
    Otherwise, execute the stage and save the result.

    Args:
        stage: Pipeline stage to execute
        artifact: Input artifact
        checkpoint: Optional Checkpoint manager (creates if not provided)
        run_dir: Directory for checkpoints if creating new

    Returns:
        PipelineArtifact (from checkpoint or fresh execution)

    Example:
        artifact = safe_run(recon_agent, None, checkpoint)
    """
    stage_name = getattr(stage, "name", str(stage))

    # Create checkpoint manager if not provided
    if checkpoint is None:
        run_id = artifact.run_id if artifact else None
        checkpoint = Checkpoint(run_dir=run_dir, run_id=run_id)

    # Check for existing checkpoint
    if checkpoint.exists(stage_name):
        print(f"[Resume] Using saved checkpoint for '{stage_name}'")
        return checkpoint.load(stage_name)

    # Execute stage
    result = stage.run(artifact)

    # Save checkpoint
    checkpoint.save(stage_name, result)

    return result


def load_artifact(checkpoint_path: str) -> PipelineArtifact:
    """
    Load an artifact from a checkpoint file.

    Convenience function matching the Listing 3.9 interface.

    Args:
        checkpoint_path: Path to the checkpoint JSON file

    Returns:
        PipelineArtifact loaded from the file
    """
    with open(checkpoint_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "timestamp" in data and isinstance(data["timestamp"], str):
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])

    return PipelineArtifact(**data)


def save_artifact(artifact: PipelineArtifact, checkpoint_path: str) -> None:
    """
    Save an artifact to a checkpoint file.

    Convenience function matching the Listing 3.9 interface.

    Args:
        artifact: Artifact to save
        checkpoint_path: Path to save the checkpoint
    """
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(artifact.to_jsonl_record(), f, indent=2)
