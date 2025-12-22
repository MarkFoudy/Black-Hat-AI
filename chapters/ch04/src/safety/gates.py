"""
Safety Gates Module (Section 4.2.4)

Provides decision checkpoints and control mechanisms that ensure
agents operate responsibly. Gates act as miniature ethics checks
before an action leaves your machine.

Gates mirror real-world red-team and assurance practices.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Callable, Optional, Tuple

from src.safety.scope import ScopeChecker


def time_window_gate(
    start_hour: int = 9,
    end_hour: int = 17,
    timezone_name: str = "UTC",
) -> Tuple[bool, str]:
    """
    Gate that only allows execution within approved hours.

    Useful for ensuring reconnaissance runs during business hours
    or other approved time windows.

    Args:
        start_hour: Start of allowed window (0-23)
        end_hour: End of allowed window (0-23)
        timezone_name: Timezone for comparison (currently only UTC supported)

    Returns:
        Tuple of (is_allowed, reason)

    Example:
        >>> allowed, reason = time_window_gate(9, 17)
        >>> if not allowed:
        ...     print(f"Blocked: {reason}")
    """
    now = datetime.now(timezone.utc)
    current_hour = now.hour

    if start_hour <= current_hour < end_hour:
        return True, f"within allowed window ({start_hour}:00-{end_hour}:00 UTC)"
    else:
        return False, f"outside allowed window ({start_hour}:00-{end_hour}:00 UTC), current: {current_hour}:00"


def approval_gate(
    action: str,
    target: str,
    auto_approve: bool = False,
    prompt_prefix: str = "[GATE]",
) -> bool:
    """
    Interactive confirmation gate before execution.

    Prompts the user for explicit approval before proceeding.
    Can be set to auto-approve for automated pipelines.

    Args:
        action: Description of the action (e.g., "scan", "probe")
        target: Target of the action (e.g., hostname)
        auto_approve: If True, skip prompt and approve automatically
        prompt_prefix: Prefix for the prompt message

    Returns:
        True if approved, False if denied

    Example:
        >>> if approval_gate("scan", "example.com"):
        ...     run_scan("example.com")
    """
    if auto_approve:
        return True

    # Check if running in non-interactive mode
    if not sys.stdin.isatty():
        print(f"{prompt_prefix} Non-interactive mode, auto-denying: {action} -> {target}")
        return False

    try:
        response = input(f"{prompt_prefix} Approve {action} -> {target}? [y/N]: ")
        return response.lower().strip() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print("\nDenied (interrupted)")
        return False


def scope_gate(
    host: str,
    checker: ScopeChecker,
) -> Tuple[bool, str]:
    """
    Gate that checks if host is within authorized scope.

    Combines scope checking with gate pattern for consistent interface.

    Args:
        host: Hostname to check
        checker: ScopeChecker instance

    Returns:
        Tuple of (is_allowed, reason)
    """
    return checker.is_allowed(host)


def rate_limit_gate(
    action_count: int,
    max_actions: int,
    window_name: str = "session",
) -> Tuple[bool, str]:
    """
    Gate that enforces rate limiting.

    Args:
        action_count: Current number of actions taken
        max_actions: Maximum allowed actions
        window_name: Name of the rate limit window for logging

    Returns:
        Tuple of (is_allowed, reason)
    """
    if action_count < max_actions:
        remaining = max_actions - action_count
        return True, f"{remaining} actions remaining in {window_name}"
    else:
        return False, f"rate limit exceeded: {action_count}/{max_actions} in {window_name}"


def environment_gate(
    required_env: str,
    expected_value: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Gate that checks for required environment configuration.

    Useful for ensuring proper setup before execution.

    Args:
        required_env: Environment variable name to check
        expected_value: If provided, also check the value matches

    Returns:
        Tuple of (is_allowed, reason)
    """
    value = os.environ.get(required_env)

    if value is None:
        return False, f"missing required environment variable: {required_env}"

    if expected_value is not None and value != expected_value:
        return False, f"{required_env} has unexpected value"

    return True, f"{required_env} is configured"


class GateChain:
    """
    Chain multiple gates together for compound checks.

    All gates must pass for the chain to pass.

    Example:
        >>> chain = GateChain()
        >>> chain.add(lambda: time_window_gate(9, 17))
        >>> chain.add(lambda: scope_gate(host, checker))
        >>> allowed, reasons = chain.check()
    """

    def __init__(self):
        """Initialize empty gate chain."""
        self.gates: list[Callable[[], Tuple[bool, str]]] = []

    def add(self, gate: Callable[[], Tuple[bool, str]]) -> "GateChain":
        """
        Add a gate to the chain.

        Args:
            gate: Callable that returns (is_allowed, reason)

        Returns:
            Self for chaining
        """
        self.gates.append(gate)
        return self

    def check(self) -> Tuple[bool, list[str]]:
        """
        Run all gates and return combined result.

        Returns:
            Tuple of (all_passed, list_of_reasons)
        """
        reasons = []
        all_passed = True

        for gate in self.gates:
            passed, reason = gate()
            reasons.append(reason)
            if not passed:
                all_passed = False

        return all_passed, reasons

    def check_and_report(self, verbose: bool = True) -> bool:
        """
        Run all gates and print results.

        Args:
            verbose: Print each gate result

        Returns:
            True if all gates passed
        """
        all_passed, reasons = self.check()

        if verbose:
            for i, (gate, reason) in enumerate(zip(self.gates, reasons)):
                status = "PASS" if "allowed" in reason.lower() or "remaining" in reason.lower() or "configured" in reason.lower() or "within" in reason.lower() else "FAIL"
                print(f"[GATE {i+1}] {status}: {reason}")

        return all_passed


def create_standard_gates(
    scope_checker: Optional[ScopeChecker] = None,
    host: Optional[str] = None,
    enable_time_gate: bool = False,
    time_start: int = 9,
    time_end: int = 17,
) -> GateChain:
    """
    Create a standard gate chain for reconnaissance.

    Args:
        scope_checker: Optional scope checker
        host: Host to check against scope
        enable_time_gate: Whether to include time window gate
        time_start: Start hour for time gate
        time_end: End hour for time gate

    Returns:
        Configured GateChain
    """
    chain = GateChain()

    if enable_time_gate:
        chain.add(lambda: time_window_gate(time_start, time_end))

    if scope_checker and host:
        chain.add(lambda: scope_gate(host, scope_checker))

    return chain
