"""
Pipeline orchestrator for multi-agent systems.

From Listing 3.4 in Black Hat AI.

The orchestrator is the conductor of your agent symphony: it is the central
coordinator that manages multiple AI agents, directing their interactions,
workflows, and tasks.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Protocol, runtime_checkable

from .artifact import PipelineArtifact
from .logger import ArtifactLogger


@runtime_checkable
class Stage(Protocol):
    """
    Protocol defining the interface for pipeline stages.

    Any class with a 'name' attribute and 'run' method can be used as a stage.
    """

    name: str

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """Execute this stage with the given input artifact."""
        ...


@runtime_checkable
class Gate(Protocol):
    """
    Protocol defining the interface for safety gates.

    Gates determine whether a stage is allowed to execute.
    """

    def allow(self, stage: Stage) -> bool:
        """Return True if the stage is allowed to execute."""
        ...


class PipelineOrchestrator:
    """
    Central coordinator that manages multiple AI agents in a pipeline.

    The orchestrator handles:
    - Task decomposition and routing
    - State management via artifacts
    - Agent coordination and sequencing
    - Safety gate enforcement
    - Artifact logging for audit trails

    From Listing 3.4 in Black Hat AI.

    Attributes:
        stages: List of stages to execute in order
        gates: List of gates to check before each stage
        run_id: Unique identifier for this pipeline run
        logger: ArtifactLogger for recording execution

    Example:
        orchestrator = PipelineOrchestrator(
            stages=[recon_agent, triage_agent, report_agent],
            gates=[GlobalGate(), ScopeGate()]
        )
        final_artifact = orchestrator.run()
    """

    def __init__(
        self,
        stages: List[Stage],
        gates: Optional[List[Gate]] = None,
        run_dir: str = "runs",
    ):
        """
        Initialize the pipeline orchestrator.

        Args:
            stages: List of stages to execute in sequence
            gates: Optional list of gates to check before each stage
            run_dir: Directory for storing artifacts
        """
        self.stages = stages
        self.gates = gates or []
        self.run_id = uuid.uuid4().hex
        self.run_dir = run_dir
        self.logger = ArtifactLogger(run_dir=run_dir, run_id=self.run_id)

    def run(self, initial_input: Optional[dict] = None) -> Optional[PipelineArtifact]:
        """
        Execute the pipeline sequentially through all stages.

        Each stage receives the artifact from the previous stage.
        Gates are checked before each stage execution.

        Args:
            initial_input: Optional initial data for the first stage

        Returns:
            The final artifact from the last stage, or None if all stages were blocked
        """
        artifact = None

        # Create initial artifact if input provided
        if initial_input:
            artifact = PipelineArtifact(
                run_id=self.run_id,
                stage="input",
                input={},
                output=initial_input,
                success=True,
            )
            self.logger.write_artifact(artifact)

        for stage in self.stages:
            # Pre-stage safety check
            if not self._check_gates(stage):
                print(f"[Gate] Stage '{stage.name}' blocked by policy.")
                self.logger.write({
                    "event": "gate_blocked",
                    "stage": stage.name,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                continue

            print(f"[Run] Executing '{stage.name}'...")

            try:
                artifact = stage.run(artifact)
                # Ensure artifact has correct run_id
                if artifact and artifact.run_id != self.run_id:
                    artifact.run_id = self.run_id
                self.logger.write_artifact(artifact)
                print(f"[Run] '{stage.name}' completed successfully.")

            except Exception as e:
                print(f"[Error] Stage '{stage.name}' failed: {e}")
                error_artifact = PipelineArtifact(
                    run_id=self.run_id,
                    stage=stage.name,
                    input=artifact.output if artifact else {},
                    output={},
                    success=False,
                    error=str(e),
                )
                self.logger.write_artifact(error_artifact)
                raise

        print(f"[Pipeline] Run {self.run_id} complete.")
        self.logger.close()
        return artifact

    def _check_gates(self, stage: Stage) -> bool:
        """
        Check all gates for a stage.

        Args:
            stage: The stage to check

        Returns:
            True if all gates allow the stage, False otherwise
        """
        return all(gate.allow(stage) for gate in self.gates)

    def get_run_id(self) -> str:
        """Return the unique run ID for this pipeline execution."""
        return self.run_id

    def get_artifact_path(self) -> str:
        """Return the path to the artifact log file."""
        return self.logger.file_path
