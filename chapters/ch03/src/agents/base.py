"""
Base stage interface for pipeline agents.

Defines the protocol that all pipeline stages must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..core.artifact import PipelineArtifact


class BaseStage(ABC):
    """
    Abstract base class for pipeline stages.

    Every stage in the pipeline must have a name and implement the run() method.
    The orchestrator calls run() with the previous stage's artifact and expects
    a new artifact in return.

    Attributes:
        name: Unique identifier for this stage
        description: Human-readable description of what this stage does

    Example:
        class MyStage(BaseStage):
            name = "my_stage"
            description = "Does something useful"

            def run(self, artifact):
                # Process input
                result = self.process(artifact.output if artifact else {})
                # Return new artifact
                return PipelineArtifact.from_previous(
                    previous=artifact,
                    stage=self.name,
                    output=result,
                    success=True
                )
    """

    name: str = "base"
    description: str = "Base pipeline stage"

    def __init__(self, name: Optional[str] = None, **config):
        """
        Initialize the stage.

        Args:
            name: Optional override for stage name
            **config: Additional configuration options
        """
        if name:
            self.name = name
        self.config: Dict[str, Any] = config

    @abstractmethod
    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """
        Execute this stage with the given input artifact.

        Args:
            artifact: Output from the previous stage (None for first stage)

        Returns:
            New PipelineArtifact containing this stage's output
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
