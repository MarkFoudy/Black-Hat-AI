"""
Retry logic with exponential backoff.

From Listing 3.8 in Black Hat AI.

Provides automatic retry for transient failures in pipeline stages.
"""

import time
from typing import Optional, Callable, Any, Type, Tuple
from dataclasses import dataclass

from ..core.artifact import PipelineArtifact


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (doubles each retry)
        max_delay: Maximum delay between retries
        retryable_exceptions: Tuple of exception types to retry
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


def retry_stage(
    stage: Any,
    artifact: Optional[PipelineArtifact],
    retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> PipelineArtifact:
    """
    Execute a pipeline stage with retry logic and exponential backoff.

    From Listing 3.8 in Black Hat AI.

    Automatically retries failed stage executions with increasing delays.
    The wait time doubles after each attempt (2s, 4s, 8s, ...) up to max_delay.

    Args:
        stage: Pipeline stage to execute (must have run() method)
        artifact: Input artifact for the stage
        retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (default: 2.0)
        max_delay: Maximum delay between retries (default: 60.0)
        on_retry: Optional callback called on each retry with (exception, attempt)

    Returns:
        PipelineArtifact from successful execution

    Raises:
        RuntimeError: If all retry attempts fail

    Example:
        artifact = retry_stage(triage_agent, recon_artifact, retries=3)
    """
    last_exception = None

    for attempt in range(retries):
        try:
            return stage.run(artifact)

        except Exception as e:
            last_exception = e
            wait = min(base_delay * (2 ** attempt), max_delay)

            stage_name = getattr(stage, "name", str(stage))
            print(f"[Retry] {stage_name} failed: {e} — retrying in {wait:.1f}s (attempt {attempt + 1}/{retries})")

            # Call retry callback if provided
            if on_retry:
                on_retry(e, attempt + 1)

            # Don't sleep after the last attempt
            if attempt < retries - 1:
                time.sleep(wait)

    stage_name = getattr(stage, "name", str(stage))
    raise RuntimeError(
        f"Stage '{stage_name}' failed after {retries} retries. Last error: {last_exception}"
    )


def retry_with_config(
    stage: Any,
    artifact: Optional[PipelineArtifact],
    config: RetryConfig,
) -> PipelineArtifact:
    """
    Execute stage with retry using a RetryConfig object.

    Args:
        stage: Pipeline stage to execute
        artifact: Input artifact
        config: RetryConfig with retry parameters

    Returns:
        PipelineArtifact from successful execution
    """
    return retry_stage(
        stage=stage,
        artifact=artifact,
        retries=config.max_retries,
        base_delay=config.base_delay,
        max_delay=config.max_delay,
    )


class RetryableStage:
    """
    Wrapper that adds retry logic to any pipeline stage.

    Example:
        retryable = RetryableStage(my_stage, max_retries=5)
        artifact = retryable.run(input_artifact)
    """

    def __init__(
        self,
        stage: Any,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        Wrap a stage with retry logic.

        Args:
            stage: The stage to wrap
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
        """
        self._stage = stage
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    @property
    def name(self) -> str:
        """Return the wrapped stage's name."""
        return getattr(self._stage, "name", "unknown")

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        """Execute the wrapped stage with retry logic."""
        return retry_stage(
            stage=self._stage,
            artifact=artifact,
            retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
        )
