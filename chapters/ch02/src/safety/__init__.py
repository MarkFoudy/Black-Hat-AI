"""
Safety and control mechanisms for AI agents.

Provides:
- Safety gate with prohibited target filtering and human confirmation
- Global kill switch for emergency stops
"""

from .gates import safety_gate
from .kill_switch import KillSwitch

__all__ = [
    "safety_gate",
    "KillSwitch",
]
