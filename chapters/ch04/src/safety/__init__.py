"""
Safety module for Chapter 4: Passive Reconnaissance Agents.

Provides scope enforcement and safety gates to ensure agents
operate within authorized boundaries.
"""

from src.safety.scope import (
    ScopeConfig,
    ScopeChecker,
    load_scope,
    load_scope_safe,
    save_scope,
    create_scope_checker,
)
from src.safety.gates import (
    time_window_gate,
    approval_gate,
    scope_gate,
    rate_limit_gate,
    environment_gate,
    GateChain,
    create_standard_gates,
)

__all__ = [
    # Scope
    "ScopeConfig",
    "ScopeChecker",
    "load_scope",
    "load_scope_safe",
    "save_scope",
    "create_scope_checker",
    # Gates
    "time_window_gate",
    "approval_gate",
    "scope_gate",
    "rate_limit_gate",
    "environment_gate",
    "GateChain",
    "create_standard_gates",
]
