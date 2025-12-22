"""
Approval gate for human-in-the-loop confirmation.

From Table 3.4 in Black Hat AI.

Requires human confirmation before execution.
"""

from typing import Any, Callable, Optional

from .base import BaseGate


class ApprovalGate(BaseGate):
    """
    Gate that requires human approval before stage execution.

    Pauses pipeline execution and waits for user confirmation.
    Essential for:
    - High-risk operations (exploit attempts, data exfiltration)
    - Compliance requirements
    - Training and demonstration scenarios

    Attributes:
        require_approval_for: List of stage names that require approval
        prompt_fn: Function to display prompt and get user input

    Example:
        gate = ApprovalGate(require_approval_for=["exploit", "exfil"])

        # Or with custom prompt
        gate = ApprovalGate(prompt_fn=my_custom_prompt)
    """

    def __init__(
        self,
        require_approval_for: Optional[list[str]] = None,
        prompt_fn: Optional[Callable[[str], str]] = None,
        auto_approve: bool = False,
    ):
        """
        Initialize the approval gate.

        Args:
            require_approval_for: List of stage names requiring approval.
                                 If None, all stages require approval.
            prompt_fn: Custom function for prompting user (default: input())
            auto_approve: If True, automatically approve all (for testing)
        """
        self.require_approval_for = require_approval_for
        self.prompt_fn = prompt_fn or input
        self.auto_approve = auto_approve

    def allow(self, stage: Any) -> bool:
        """
        Request human approval for the stage.

        Args:
            stage: The pipeline stage requesting permission

        Returns:
            True if user approves, False otherwise
        """
        stage_name = getattr(stage, "name", str(stage))

        # Check if this stage requires approval
        if self.require_approval_for is not None:
            if stage_name not in self.require_approval_for:
                return True

        # Auto-approve if configured (for testing)
        if self.auto_approve:
            print(f"[ApprovalGate] Auto-approved '{stage_name}'")
            return True

        # Get stage description if available
        description = getattr(stage, "description", f"Execute stage '{stage_name}'")

        # Prompt for approval
        print(f"\n{'='*60}")
        print(f"[ApprovalGate] Approval required for: {stage_name}")
        print(f"Description: {description}")
        print(f"{'='*60}")

        try:
            response = self.prompt_fn(f"Approve execution of '{stage_name}'? (y/n): ")
            approved = response.lower().strip() in ("y", "yes")

            if approved:
                print(f"[ApprovalGate] Approved: {stage_name}")
            else:
                print(f"[ApprovalGate] Denied: {stage_name}")

            return approved

        except (EOFError, KeyboardInterrupt):
            print(f"\n[ApprovalGate] Approval cancelled for '{stage_name}'")
            return False

    def __repr__(self) -> str:
        return f"ApprovalGate(require_approval_for={self.require_approval_for})"
