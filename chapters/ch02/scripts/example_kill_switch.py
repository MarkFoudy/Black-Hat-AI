#!/usr/bin/env python3
"""
Kill switch demonstration.

Shows the Listing 2.10 idiom: start the switch, run a loop that checks
.is_active, and exit cleanly when STOP is entered on stdin.

Run from the ch02 directory:
    python scripts/example_kill_switch.py

Then type STOP and press Enter to trigger the kill switch.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.safety.kill_switch import KillSwitch


def main():
    kill_switch = KillSwitch()
    kill_switch.start()

    step = 0
    while not kill_switch.is_active:
        step += 1
        print(f"[Agent] Running step {step} ...")
        time.sleep(1)

    print("[Agent] Kill switch activated — shutting down cleanly.")


if __name__ == "__main__":
    main()
