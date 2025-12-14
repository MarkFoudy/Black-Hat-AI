"""
Safety and control mechanisms for AI agents.

Provides:
- Safety gates with prohibited target filtering
- Human-in-the-loop confirmation
- Global kill switch for emergency stops
"""

from .gates import safety_gate, simple_gate
from .kill_switch import KillSwitch

__all__ = [
    "safety_gate",
    "simple_gate",
    "KillSwitch",
]
