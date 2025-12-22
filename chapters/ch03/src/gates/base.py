"""
Base gate interface for safety gates.

Provides the abstract base class that all gates must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Stage(Protocol):
    """Protocol for pipeline stages."""

    name: str


class BaseGate(ABC):
    """
    Abstract base class for safety gates.

    Gates determine whether a pipeline stage is allowed to execute.
    They are checked by the orchestrator before each stage runs.

    Subclasses must implement the allow() method to define their
    specific approval logic.

    Example:
        class MyGate(BaseGate):
            def allow(self, stage: Stage) -> bool:
                # Custom logic here
                return True
    """

    @abstractmethod
    def allow(self, stage: Any) -> bool:
        """
        Determine if a stage is allowed to execute.

        Args:
            stage: The pipeline stage requesting permission

        Returns:
            True if the stage is allowed to proceed, False otherwise
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
