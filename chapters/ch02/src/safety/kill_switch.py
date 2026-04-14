"""
Global kill switch for emergency agent termination.

From Listing 2.10 in Black Hat AI.

Provides a background monitoring thread that allows operators to
immediately stop all agent activity in emergency situations.
"""

import threading
from typing import Optional


class KillSwitch:
    """
    Emergency stop mechanism for AI agent operations.

    Runs a daemon thread that monitors stdin for the "STOP" command.
    When activated, sets a threading.Event that agents check via the
    is_active property to terminate their loops cleanly.

    All agents should check .is_active inside their loops to honor
    the abort signal.

    Example:
        kill_switch = KillSwitch()
        kill_switch.start()

        while not kill_switch.is_active:
            perform_action()

    Note:
        - Monitor thread runs as daemon (won't prevent program exit)
        - Type "STOP" (case-insensitive) to activate
        - Once activated, cannot be deactivated (safety feature)
        - EOFError is handled gracefully for non-interactive stdin
    """

    def __init__(self) -> None:
        """Initialize the kill switch in inactive state."""
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None

    @property
    def is_active(self) -> bool:
        """Return True if the kill switch has been activated."""
        return self._stop_event.is_set()

    def _monitor(self) -> None:
        """
        Monitor loop that runs in background daemon thread.

        Waits for "STOP" input and sets the stop event when received.
        Handles EOFError for non-interactive stdin (pipes, test harnesses).
        """
        while not self._stop_event.is_set():
            try:
                cmd = input("[KillSwitch] Type 'STOP' to abort: ")
                if cmd.strip().upper() == "STOP":
                    self._stop_event.set()
                    print("[KillSwitch] ACTIVATED — aborting all agents.")
                    break
            except EOFError:
                break

    def start(self) -> None:
        """
        Start the kill switch monitor in a background daemon thread.

        Raises:
            RuntimeError: If monitor is already running
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            raise RuntimeError("Kill switch monitor is already running")

        self._monitor_thread = threading.Thread(
            target=self._monitor, daemon=True
        )
        self._monitor_thread.start()
        print("[KillSwitch] Monitor started (type STOP to abort)")

    def __enter__(self):
        """Context manager entry - starts monitoring."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
