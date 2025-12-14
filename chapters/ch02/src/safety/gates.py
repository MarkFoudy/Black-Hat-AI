"""
Safety gates for human-in-the-loop control of AI agents.

From Listings 2.10 and 2.14 in Black Hat AI.

Provides safety mechanisms to prevent agents from performing dangerous
actions without human approval. Critical for offensive security tools.
"""

from typing import Dict, Any, List, Optional
import os


def safety_gate(action: str, context: Dict[str, Any]) -> bool:
    """
    Advanced safety gate with prohibited target filtering and user confirmation.

    From Listing 2.10 in Black Hat AI.

    This gate provides two layers of protection:
    1. Automatic blocking of prohibited targets (e.g., production systems)
    2. Human confirmation for all other actions

    Args:
        action: Description of the action to be performed
        context: Dictionary containing action context (must include "target" key)

    Returns:
        True if action is approved to proceed, False otherwise

    Example:
        if safety_gate("ping", {"target": "example.com"}):
            # Perform the action
            pass
        else:
            print("Action blocked by safety gate")

    Note:
        Prohibited hosts can be configured via PROHIBITED_HOSTS environment
        variable (comma-separated) or defaults to production-critical systems.
    """
    # Get prohibited hosts from environment or use defaults
    prohibited_str = os.getenv("PROHIBITED_HOSTS", "prod,payment,core-db")
    prohibited_hosts = [h.strip() for h in prohibited_str.split(",")]

    # Check if target contains any prohibited keywords
    target = context.get("target", "")
    if any(p in target for p in prohibited_hosts):
        print(f"[Gate] ⛔ Blocked unsafe target: {target}")
        print(f"[Gate] Prohibited hosts: {', '.join(prohibited_hosts)}")
        return False

    # Request human confirmation
    confirm = input(f"[Gate] Approve '{action}' on {target}? (y/n): ")
    approved = confirm.lower().startswith("y")

    if approved:
        print(f"[Gate] ✓ Approved: {action} on {target}")
    else:
        print(f"[Gate] ✗ Denied: {action} on {target}")

    return approved


def simple_gate(action: str, context: Dict[str, Any]) -> bool:
    """
    Simplified safety gate with only user confirmation.

    From Listing 2.14 in Black Hat AI.

    A streamlined version that provides basic human-in-the-loop control
    without automatic filtering. Useful for development and testing.

    Args:
        action: Description of the action to be performed
        context: Dictionary containing action context

    Returns:
        True if action is approved, False otherwise

    Example:
        if simple_gate("scan_ports", {"target": "192.168.1.1"}):
            # Perform the scan
            pass

    Note:
        This is the minimal safety gate. For production use, consider
        the full safety_gate() function with prohibited target filtering.
    """
    target = context.get("target", "unknown")
    confirm = input(f"[Gate] Approve '{action}' on {target}? (y/n): ")
    return confirm.lower().startswith("y")


def batch_safety_gate(
    actions: List[tuple[str, Dict[str, Any]]], allow_batch_approval: bool = True
) -> List[bool]:
    """
    Safety gate for approving multiple actions at once.

    Useful for agents that plan multiple steps in advance.

    Args:
        actions: List of (action, context) tuples to approve
        allow_batch_approval: If True, allow approving all at once

    Returns:
        List of boolean approval decisions (same length as actions)

    Example:
        actions = [
            ("ping", {"target": "example.com"}),
            ("scan", {"target": "example.com"}),
        ]
        approvals = batch_safety_gate(actions)
        for (action, context), approved in zip(actions, approvals):
            if approved:
                perform_action(action, context)
    """
    if not actions:
        return []

    print(f"\n[Gate] Reviewing {len(actions)} proposed actions:")
    for i, (action, context) in enumerate(actions, 1):
        target = context.get("target", "unknown")
        print(f"  {i}. {action} on {target}")

    if allow_batch_approval:
        batch = input("\n[Gate] Approve all? (y/n/individual): ").lower()
        if batch.startswith("y"):
            print("[Gate] ✓ All actions approved")
            return [True] * len(actions)
        elif batch.startswith("n"):
            print("[Gate] ✗ All actions denied")
            return [False] * len(actions)

    # Individual approval
    print("\n[Gate] Reviewing individually:")
    approvals = []
    for action, context in actions:
        approved = safety_gate(action, context)
        approvals.append(approved)

    return approvals
