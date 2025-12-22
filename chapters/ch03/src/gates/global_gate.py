"""
Global gate for time-based pipeline restrictions.

From Listing 3.6 in Black Hat AI.

Global gates enforce organization-wide or engagement-wide policy decisions.
They determine whether a stage may even run based on time, scope, or approval status.
"""

from datetime import datetime
from typing import Any, Optional

from .base import BaseGate


class GlobalGate(BaseGate):
    """
    Time-based gate that restricts execution outside business hours.

    From Listing 3.6 in Black Hat AI.

    This gate prevents pipeline stages from running during off-hours,
    which is useful for:
    - Respecting testing windows in client engagements
    - Avoiding scans during high-traffic periods
    - Ensuring human oversight is available

    Attributes:
        start_hour: Hour (UTC) when operations are allowed to start (default: 7)
        end_hour: Hour (UTC) when operations must stop (default: 22)

    Example:
        gate = GlobalGate()  # Default: allow 07:00-22:00 UTC
        gate = GlobalGate(start_hour=9, end_hour=17)  # 9-5 only
    """

    def __init__(
        self,
        start_hour: int = 7,
        end_hour: int = 22,
        enabled: bool = True,
    ):
        """
        Initialize the global gate.

        Args:
            start_hour: Hour (0-23 UTC) when operations can begin
            end_hour: Hour (0-23 UTC) when operations must stop
            enabled: Whether this gate is active (default: True)
        """
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.enabled = enabled

    def allow(self, stage: Any) -> bool:
        """
        Check if current time is within the allowed window.

        Args:
            stage: The pipeline stage (not used for time-based check)

        Returns:
            True if current UTC hour is within allowed window
        """
        if not self.enabled:
            return True

        hour = datetime.utcnow().hour

        # Handle overnight windows (e.g., 22:00 to 06:00)
        if self.start_hour <= self.end_hour:
            # Normal window (e.g., 07:00 to 22:00)
            allowed = self.start_hour <= hour < self.end_hour
        else:
            # Overnight window (e.g., 22:00 to 06:00)
            allowed = hour >= self.start_hour or hour < self.end_hour

        if not allowed:
            stage_name = getattr(stage, "name", str(stage))
            print(
                f"[GlobalGate] Blocked '{stage_name}': "
                f"current hour {hour} outside window {self.start_hour:02d}:00-{self.end_hour:02d}:00 UTC"
            )

        return allowed

    def __repr__(self) -> str:
        return f"GlobalGate(start_hour={self.start_hour}, end_hour={self.end_hour}, enabled={self.enabled})"
