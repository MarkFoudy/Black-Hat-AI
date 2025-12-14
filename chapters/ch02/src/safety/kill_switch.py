"""
Global kill switch for emergency agent termination.

From Listing 2.16 in Black Hat AI.

Provides a background monitoring thread that allows operators to
immediately stop all agent activity in emergency situations.
"""

import threading
import time
from typing import Optional


class KillSwitch:
    """
    Emergency stop mechanism for AI agent operations.

    Runs a background thread that continuously monitors for the "STOP"
    command. When activated, sets a flag that agents can check to
    terminate their operations immediately.

    This is critical for offensive security tools where agents might
    take unexpected or dangerous actions.

    Attributes:
        active: Boolean flag indicating if kill switch has been activated
        _monitor_thread: Background thread running the monitor

    Example:
        kill_switch = KillSwitch()
        kill_switch.start()

        # In agent loop:
        while not kill_switch.active:
            perform_action()
            if kill_switch.active:
                break

        kill_switch.stop()

    Note:
        - Monitor thread runs as daemon (won't prevent program exit)
        - Type "STOP" (case-insensitive) to activate
        - Once activated, cannot be deactivated (safety feature)
    """

    def __init__(self) -> None:
        """Initialize the kill switch in inactive state."""
        self.active = False
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

    def monitor(self) -> None:
        """
        Monitor loop that runs in background thread.

        Continuously prompts for input and activates kill switch
        when "STOP" is entered.

        Note:
            This method blocks and should be run in a separate thread.
            Use start() to begin monitoring automatically.
        """
        while self._running:
            try:
                cmd = input("[KillSwitch] Type 'STOP' to abort: ")
                if cmd.strip().upper() == "STOP":
                    self.active = True
                    print("[KillSwitch] ⛔ ACTIVATED - Aborting all agents.")
                    break
            except (EOFError, KeyboardInterrupt):
                # Handle gracefully if stdin is closed or Ctrl+C
                break

    def start(self) -> None:
        """
        Start the kill switch monitor in a background thread.

        The monitor thread runs as a daemon, so it won't prevent
        the program from exiting.

        Raises:
            RuntimeError: If monitor is already running
        """
        if self._running:
            raise RuntimeError("Kill switch monitor is already running")

        self._running = True
        self._monitor_thread = threading.Thread(target=self.monitor, daemon=True)
        self._monitor_thread.start()
        print("[KillSwitch] ✓ Monitor started (type STOP to abort)")

    def stop(self) -> None:
        """
        Stop the kill switch monitor thread.

        Note:
            This stops the monitoring, but does not deactivate the
            kill switch if it has already been activated.
        """
        self._running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            # Give thread time to finish
            self._monitor_thread.join(timeout=1.0)

    def check(self) -> bool:
        """
        Check if kill switch has been activated.

        Returns:
            True if kill switch is active, False otherwise

        Example:
            kill_switch = KillSwitch()
            kill_switch.start()

            for target in targets:
                if kill_switch.check():
                    print("Operation aborted by kill switch")
                    break
                process_target(target)
        """
        return self.active

    def __enter__(self):
        """Context manager entry - starts monitoring."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stops monitoring."""
        self.stop()
