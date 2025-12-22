"""
Time window gate for business hours enforcement.

From Table 3.4 in Black Hat AI.

Restricts when operations can occur based on day of week and time.
"""

from datetime import datetime, time
from typing import Any, List, Optional

from .base import BaseGate


class TimeWindowGate(BaseGate):
    """
    Gate that enforces specific time windows for operations.

    More granular than GlobalGate - allows specifying:
    - Specific days of the week
    - Start and end times with minutes
    - Timezone-aware checks (via UTC offset)

    Useful for:
    - Testing only during maintenance windows
    - Respecting client business hours
    - Coordinating with SOC staffing schedules

    Attributes:
        start_time: Time operations can begin
        end_time: Time operations must stop
        allowed_days: List of allowed weekdays (0=Monday, 6=Sunday)

    Example:
        # Monday-Friday, 9:00 AM to 5:00 PM
        gate = TimeWindowGate(
            start_time=time(9, 0),
            end_time=time(17, 0),
            allowed_days=[0, 1, 2, 3, 4]
        )
    """

    def __init__(
        self,
        start_time: time = time(9, 0),
        end_time: time = time(17, 0),
        allowed_days: Optional[List[int]] = None,
        utc_offset_hours: int = 0,
    ):
        """
        Initialize the time window gate.

        Args:
            start_time: Time when operations can begin
            end_time: Time when operations must stop
            allowed_days: List of weekday numbers (0=Monday, 6=Sunday)
                         Default: Monday-Friday
            utc_offset_hours: Hours to offset from UTC for local time
        """
        self.start_time = start_time
        self.end_time = end_time
        self.allowed_days = allowed_days if allowed_days is not None else [0, 1, 2, 3, 4]
        self.utc_offset_hours = utc_offset_hours

    def allow(self, stage: Any) -> bool:
        """
        Check if current time is within the allowed window.

        Args:
            stage: The pipeline stage requesting permission

        Returns:
            True if current time is within allowed window and day
        """
        now = datetime.utcnow()

        # Apply timezone offset
        from datetime import timedelta
        local_now = now + timedelta(hours=self.utc_offset_hours)

        # Check day of week
        if local_now.weekday() not in self.allowed_days:
            stage_name = getattr(stage, "name", str(stage))
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            print(
                f"[TimeWindowGate] Blocked '{stage_name}': "
                f"{day_names[local_now.weekday()]} not in allowed days"
            )
            return False

        # Check time of day
        current_time = local_now.time()
        if not (self.start_time <= current_time < self.end_time):
            stage_name = getattr(stage, "name", str(stage))
            print(
                f"[TimeWindowGate] Blocked '{stage_name}': "
                f"{current_time.strftime('%H:%M')} outside window "
                f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
            )
            return False

        return True

    def __repr__(self) -> str:
        return (
            f"TimeWindowGate(start={self.start_time}, end={self.end_time}, "
            f"days={self.allowed_days})"
        )
