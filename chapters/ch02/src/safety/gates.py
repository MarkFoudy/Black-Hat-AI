"""
Safety gate for human-in-the-loop control of AI agents.

From Listing 2.8 in Black Hat AI.

Provides a safety mechanism to prevent agents from performing dangerous
actions without human approval. Critical for offensive security tools.
"""

from typing import Dict, Any


def safety_gate(action: str, context: Dict[str, Any]) -> bool:
    """
    Safety gate with prohibited target filtering and user confirmation.

    From Listing 2.8 in Black Hat AI.

    This gate provides two layers of protection:
    1. Automatic blocking of prohibited targets (exact hostname match)
    2. Human confirmation for all other actions

    The exact-match check is intentional: substring matching would
    false-positive a host like "nonproduction.internal" against the
    pattern "prod".

    Args:
        action: Description of the action to be performed
        context: Dictionary containing action context (must include "target" key)

    Returns:
        True if action is approved to proceed, False otherwise

    Example:
        if safety_gate("scan", {"target": "example.com"}):
            perform_action()
        else:
            print("Action blocked by safety gate")
    """
    prohibited_targets = {
        "prod.example.com",
        "payment.example.com",
        "core-db.example.com",
    }

    target = context.get("target", "")

    if target in prohibited_targets:
        print(f"[Gate] BLOCKED: {target}")
        return False

    confirm = input(f"[Gate] Approve '{action}' on {target}? (y/n): ")
    return confirm.lower().startswith("y")
