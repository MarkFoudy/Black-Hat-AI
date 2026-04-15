"""
Global kill switch for emergency agent termination.

From Listing 2.10 in Black Hat AI.

Provides a background monitoring thread that allows operators to
immediately stop all agent activity in emergency situations.
"""

import threading


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
    """

    def __init__(self) -> None:
        self._stop_event = threading.Event()

    @property
    def is_active(self) -> bool:
        return self._stop_event.is_set()

    def _monitor(self) -> None:
        while not self._stop_event.is_set():
            try:
                cmd = input()
                if cmd.strip().upper() == "STOP":
                    self._stop_event.set()
                    print("[KillSwitch] ACTIVATED — aborting all agents.")
                    break
            except EOFError:
                break

    def start(self) -> None:
        threading.Thread(target=self._monitor, daemon=True).start()
