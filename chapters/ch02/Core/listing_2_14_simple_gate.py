def safety_gate(action: str, context: dict) -> bool:
    """Return True if action is approved to proceed."""
    prohibited_hosts = ["prod", "payment", "core-db"]
    if any(p in context.get("target", "") for p in prohibited_hosts):
        print(f"[Gate] Blocked unsafe target: {context['target']}")
        return False
    confirm = input(f"[Gate] Approve '{action}' on {context['target']}? (y/n): ")
    return confirm.lower().startswith("y")
