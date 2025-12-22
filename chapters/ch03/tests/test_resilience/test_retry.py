"""
Tests for retry and resilience patterns.

From Listings 3.8, 3.9, 3.10 in Black Hat AI.
"""

import pytest
from typing import Optional

from src.resilience import retry_stage, Checkpoint, AlertHandler
from src.core.artifact import PipelineArtifact


class TestRetryStage:
    """Tests for retry_stage function (Listing 3.8)."""

    def test_succeeds_first_try(self):
        """Test successful execution without retries."""

        class SuccessStage:
            name = "success"

            def run(self, artifact):
                return PipelineArtifact(
                    stage=self.name,
                    input={},
                    output={"result": "ok"},
                    success=True,
                )

        stage = SuccessStage()
        result = retry_stage(stage, None, retries=3)

        assert result.success is True

    def test_retries_on_failure(self):
        """Test that failures trigger retries."""

        class FlakyStage:
            name = "flaky"
            attempts = 0

            def run(self, artifact):
                self.attempts += 1
                if self.attempts < 3:
                    raise ConnectionError("Simulated failure")
                return PipelineArtifact(
                    stage=self.name,
                    input={},
                    output={"attempts": self.attempts},
                    success=True,
                )

        stage = FlakyStage()
        result = retry_stage(stage, None, retries=3, base_delay=0.01)

        assert result.success is True
        assert stage.attempts == 3

    def test_raises_after_max_retries(self):
        """Test that RuntimeError is raised after all retries fail."""

        class FailStage:
            name = "fail"

            def run(self, artifact):
                raise ValueError("Always fails")

        stage = FailStage()

        with pytest.raises(RuntimeError, match="failed after 3 retries"):
            retry_stage(stage, None, retries=3, base_delay=0.01)

    def test_callback_on_retry(self):
        """Test that retry callback is called."""
        callbacks = []

        class FlakyStage:
            name = "flaky"
            attempts = 0

            def run(self, artifact):
                self.attempts += 1
                if self.attempts < 2:
                    raise ConnectionError("Fail once")
                return PipelineArtifact(
                    stage=self.name,
                    input={},
                    output={},
                    success=True,
                )

        def on_retry(error, attempt):
            callbacks.append((str(error), attempt))

        stage = FlakyStage()
        retry_stage(stage, None, retries=3, base_delay=0.01, on_retry=on_retry)

        assert len(callbacks) == 1
        assert callbacks[0][1] == 1


class TestCheckpoint:
    """Tests for Checkpoint class (Listing 3.9)."""

    @pytest.fixture
    def checkpoint_dir(self, tmp_path):
        """Create temporary checkpoint directory."""
        return str(tmp_path / "checkpoints")

    def test_save_and_load(self, checkpoint_dir):
        """Test saving and loading checkpoints."""
        checkpoint = Checkpoint(run_dir=checkpoint_dir)

        artifact = PipelineArtifact(
            stage="test",
            input={"data": "input"},
            output={"result": "output"},
            success=True,
        )

        checkpoint.save("test", artifact)
        assert checkpoint.exists("test")

        loaded = checkpoint.load("test")
        assert loaded.stage == "test"
        assert loaded.output == {"result": "output"}

    def test_load_nonexistent(self, checkpoint_dir):
        """Test loading non-existent checkpoint."""
        checkpoint = Checkpoint(run_dir=checkpoint_dir)

        result = checkpoint.load("nonexistent")
        assert result is None

    def test_clear_stage(self, checkpoint_dir):
        """Test clearing a specific stage checkpoint."""
        checkpoint = Checkpoint(run_dir=checkpoint_dir)

        artifact = PipelineArtifact(
            stage="test",
            input={},
            output={},
            success=True,
        )

        checkpoint.save("test", artifact)
        assert checkpoint.exists("test")

        checkpoint.clear("test")
        assert not checkpoint.exists("test")

    def test_list_stages(self, checkpoint_dir):
        """Test listing checkpointed stages."""
        checkpoint = Checkpoint(run_dir=checkpoint_dir)

        for name in ["stage_a", "stage_b", "stage_c"]:
            artifact = PipelineArtifact(
                stage=name,
                input={},
                output={},
                success=True,
            )
            checkpoint.save(name, artifact)

        stages = checkpoint.list_stages()
        assert set(stages) == {"stage_a", "stage_b", "stage_c"}


class TestAlertHandler:
    """Tests for AlertHandler class (Listing 3.10)."""

    def test_record_error(self):
        """Test error recording."""
        handler = AlertHandler()

        handler.record_error("test_stage", ValueError("test error"))

        assert handler.get_error_count("test_stage") == 1
        assert handler.get_error_count() == 1

    def test_threshold_alert(self):
        """Test that alert is triggered at threshold."""
        from src.resilience.alerts import AlertConfig

        config = AlertConfig(error_threshold=3)
        handler = AlertHandler(config)

        for i in range(3):
            handler.record_error("stage", ValueError(f"error {i}"))

        assert len(handler.alert_history) == 1

    def test_reset_counts(self):
        """Test resetting error counts."""
        handler = AlertHandler()

        handler.record_error("stage", ValueError("error"))
        assert handler.get_error_count("stage") == 1

        handler.reset("stage")
        assert handler.get_error_count("stage") == 0

    def test_alert_callback(self):
        """Test that alert callback is called."""
        from src.resilience.alerts import AlertConfig

        alerts = []

        def callback(message, alert):
            alerts.append((message, alert))

        config = AlertConfig(error_threshold=1, alert_callback=callback)
        handler = AlertHandler(config)

        handler.record_error("stage", ValueError("error"))

        assert len(alerts) == 1
        assert "threshold exceeded" in alerts[0][0]
