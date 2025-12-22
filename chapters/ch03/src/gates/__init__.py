"""
Safety gates for multi-agent pipeline governance.

This module provides gate implementations that control when and whether
pipeline stages are allowed to execute. Gates embed governance directly
into the orchestration layer.

Gate Types:
- GlobalGate: Time-based restrictions (Listing 3.6)
- ScopeGate: Authorized target filtering
- TimeWindowGate: Business hours enforcement
- ApprovalGate: Human-in-the-loop confirmation
- EnvironmentGate: Production system blocking (Listing 3.5)
"""

from .base import BaseGate
from .global_gate import GlobalGate
from .scope_gate import ScopeGate
from .time_window_gate import TimeWindowGate
from .approval_gate import ApprovalGate
from .environment_gate import EnvironmentGate

__all__ = [
    "BaseGate",
    "GlobalGate",
    "ScopeGate",
    "TimeWindowGate",
    "ApprovalGate",
    "EnvironmentGate",
]
