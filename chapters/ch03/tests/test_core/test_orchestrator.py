"""
Tests for PipelineOrchestrator.

From Listing 3.4 in Black Hat AI.
"""

import pytest
import os
import shutil
from typing import Optional

from src.core.orchestrator import PipelineOrchestrator
from src.core.artifact import PipelineArtifact


class MockStage:
    """Simple stage for testing."""

    def __init__(self, name: str, output: dict = None, should_fail: bool = False):
        self.name = name
        self._output = output or {"result": f"{name}_done"}
        self._should_fail = should_fail

    def run(self, artifact: Optional[PipelineArtifact]) -> PipelineArtifact:
        if self._should_fail:
            raise RuntimeError(f"{self.name} failed intentionally")

        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output=self._output,
            success=True,
        )


class MockGate:
    """Simple gate for testing."""

    def __init__(self, allow_all: bool = True, blocked_stages: list = None):
        self._allow_all = allow_all
        self._blocked = blocked_stages or []

    def allow(self, stage) -> bool:
        if not self._allow_all:
            return False
        return stage.name not in self._blocked


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator class."""

    @pytest.fixture
    def run_dir(self, tmp_path):
        """Create temporary run directory."""
        return str(tmp_path / "runs")

    def test_create_orchestrator(self, run_dir):
        """Test orchestrator creation."""
        stages = [MockStage("a"), MockStage("b")]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)

        assert orchestrator.stages == stages
        assert orchestrator.run_id is not None
        assert len(orchestrator.gates) == 0

    def test_run_sequential_pipeline(self, run_dir):
        """Test running stages in sequence."""
        stages = [
            MockStage("recon", {"hosts": ["host1"]}),
            MockStage("triage", {"risk": "high"}),
            MockStage("report", {"path": "report.md"}),
        ]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)
        result = orchestrator.run()

        assert result is not None
        assert result.stage == "report"
        assert result.success is True

    def test_run_with_initial_input(self, run_dir):
        """Test pipeline with initial input."""
        stages = [MockStage("process")]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)
        result = orchestrator.run(initial_input={"targets": ["example.com"]})

        assert result is not None
        # The input stage artifact should have our data

    def test_gate_blocks_stage(self, run_dir):
        """Test that blocked stages are skipped."""
        stages = [
            MockStage("allowed"),
            MockStage("blocked"),
            MockStage("also_allowed"),
        ]
        gate = MockGate(blocked_stages=["blocked"])

        orchestrator = PipelineOrchestrator(
            stages=stages,
            gates=[gate],
            run_dir=run_dir,
        )
        result = orchestrator.run()

        # Pipeline should complete but skip blocked stage
        assert result is not None
        assert result.stage == "also_allowed"

    def test_all_gates_must_pass(self, run_dir):
        """Test that all gates must allow for stage to run."""
        stages = [MockStage("test")]
        gate1 = MockGate(allow_all=True)
        gate2 = MockGate(allow_all=False)

        orchestrator = PipelineOrchestrator(
            stages=stages,
            gates=[gate1, gate2],
            run_dir=run_dir,
        )
        result = orchestrator.run()

        # Stage should be blocked
        assert result is None

    def test_stage_failure_raises(self, run_dir):
        """Test that stage failures are propagated."""
        stages = [
            MockStage("good"),
            MockStage("bad", should_fail=True),
        ]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)

        with pytest.raises(RuntimeError, match="bad failed"):
            orchestrator.run()

    def test_artifact_logging(self, run_dir):
        """Test that artifacts are logged to file."""
        stages = [MockStage("test")]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)
        orchestrator.run()

        artifact_path = orchestrator.get_artifact_path()
        assert os.path.exists(artifact_path)

        # Check file has content
        with open(artifact_path) as f:
            content = f.read()
            assert "test" in content

    def test_run_id_consistency(self, run_dir):
        """Test that run_id is consistent across artifacts."""
        stages = [MockStage("a"), MockStage("b"), MockStage("c")]

        orchestrator = PipelineOrchestrator(stages=stages, run_dir=run_dir)
        result = orchestrator.run()

        assert result.run_id == orchestrator.run_id
