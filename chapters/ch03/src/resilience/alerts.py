"""
Alert and monitoring hooks for pipeline observability.

From Listing 3.10 in Black Hat AI.

Provides error counting, threshold alerts, and monitoring integration.
"""

from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class AlertConfig:
    """
    Configuration for alert thresholds.

    Attributes:
        error_threshold: Number of errors before alerting
        warning_threshold: Number of warnings before alerting
        alert_callback: Function to call when threshold exceeded
    """

    error_threshold: int = 5
    warning_threshold: int = 10
    alert_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None


class AlertHandler:
    """
    Manages error counting and threshold-based alerting.

    Tracks errors across pipeline stages and triggers alerts when
    configurable thresholds are exceeded.

    Attributes:
        config: AlertConfig with thresholds
        error_counts: Dictionary of error counts by stage
        alert_history: List of triggered alerts

    Example:
        handler = AlertHandler(AlertConfig(error_threshold=3))
        handler.record_error("recon", Exception("timeout"))
        if handler.should_alert("recon"):
            handler.send_alert("recon", "Too many errors")
    """

    def __init__(self, config: Optional[AlertConfig] = None):
        """
        Initialize the alert handler.

        Args:
            config: AlertConfig (uses defaults if not provided)
        """
        self.config = config or AlertConfig()
        self.error_counts: Dict[str, int] = {}
        self.warning_counts: Dict[str, int] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self._total_errors = 0

    def record_error(
        self,
        stage_name: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an error for a stage.

        Args:
            stage_name: Name of the stage that errored
            error: The exception that occurred
            context: Optional additional context
        """
        self.error_counts[stage_name] = self.error_counts.get(stage_name, 0) + 1
        self._total_errors += 1

        print(
            f"[Alert] Error #{self.error_counts[stage_name]} in '{stage_name}': {error}"
        )

        # Check if we should alert
        if self.should_alert(stage_name):
            self.send_alert(
                stage_name,
                f"Error threshold exceeded: {self.error_counts[stage_name]} errors",
                {"error": str(error), **(context or {})},
            )

    def record_warning(self, stage_name: str, message: str) -> None:
        """Record a warning for a stage."""
        self.warning_counts[stage_name] = self.warning_counts.get(stage_name, 0) + 1
        print(f"[Warn] {stage_name}: {message}")

    def should_alert(self, stage_name: str) -> bool:
        """Check if error count exceeds threshold."""
        return self.error_counts.get(stage_name, 0) >= self.config.error_threshold

    def send_alert(
        self,
        stage_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send an alert (log + callback).

        Args:
            stage_name: Stage that triggered the alert
            message: Alert message
            context: Additional context
        """
        alert = {
            "stage": stage_name,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "error_count": self.error_counts.get(stage_name, 0),
            "context": context or {},
        }

        self.alert_history.append(alert)
        print(f"[ALERT] {stage_name}: {message}")

        # Call callback if configured
        if self.config.alert_callback:
            self.config.alert_callback(message, alert)

    def get_error_count(self, stage_name: Optional[str] = None) -> int:
        """Get error count for a stage or total."""
        if stage_name:
            return self.error_counts.get(stage_name, 0)
        return self._total_errors

    def reset(self, stage_name: Optional[str] = None) -> None:
        """Reset error counts."""
        if stage_name:
            self.error_counts.pop(stage_name, None)
        else:
            self.error_counts.clear()
            self._total_errors = 0


# Global alert handler for simple usage
_global_handler: Optional[AlertHandler] = None


def get_alert_handler() -> AlertHandler:
    """Get or create the global alert handler."""
    global _global_handler
    if _global_handler is None:
        _global_handler = AlertHandler()
    return _global_handler


def send_alert(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Send a simple alert.

    From Listing 3.10 in Black Hat AI:
        if error_count > 5:
            send_alert(f"Pipeline {run_id} failing repeatedly")

    Args:
        message: Alert message
        context: Optional additional context

    Example:
        if error_count > 5:
            send_alert(f"Pipeline {run_id} failing repeatedly")
    """
    handler = get_alert_handler()

    alert = {
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "context": context or {},
    }

    handler.alert_history.append(alert)
    print(f"[ALERT] {message}")

    if handler.config.alert_callback:
        handler.config.alert_callback(message, alert)


def check_and_alert(
    error_count: int,
    run_id: str,
    threshold: int = 5,
) -> bool:
    """
    Check error count and send alert if threshold exceeded.

    Convenience function matching Listing 3.10 pattern.

    Args:
        error_count: Current error count
        run_id: Pipeline run ID
        threshold: Error threshold for alerting

    Returns:
        True if alert was sent, False otherwise

    Example:
        if check_and_alert(error_count, run_id, threshold=5):
            # Alert was sent, handle accordingly
            pass
    """
    if error_count > threshold:
        send_alert(
            f"Pipeline {run_id} failing repeatedly",
            {"error_count": error_count, "threshold": threshold},
        )
        return True
    return False
