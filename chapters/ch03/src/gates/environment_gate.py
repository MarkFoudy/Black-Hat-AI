"""
Environment gate for production system blocking.

From Listing 3.5 in Black Hat AI.

Blocks actions in production or sensitive systems.
"""

import os
from typing import Any, List, Optional, Set

from .base import BaseGate


class EnvironmentGate(BaseGate):
    """
    Gate that blocks operations on production or sensitive systems.

    From Listing 3.5 in Black Hat AI.

    Implements local gate logic that prevents targeting production
    systems, payment processors, databases, and other critical
    infrastructure.

    Attributes:
        prohibited_patterns: Set of patterns to block
        check_hostname: Whether to check system hostname
        check_targets: Whether to check stage targets

    Example:
        gate = EnvironmentGate()  # Uses default patterns

        # Custom patterns
        gate = EnvironmentGate(prohibited_patterns=["prod", "live", "customer"])
    """

    DEFAULT_PROHIBITED = {"prod", "payment", "core-db", "production", "live"}

    def __init__(
        self,
        prohibited_patterns: Optional[List[str]] = None,
        check_hostname: bool = True,
        check_targets: bool = True,
    ):
        """
        Initialize the environment gate.

        Args:
            prohibited_patterns: List of patterns to block.
                               Defaults to env var PROHIBITED_HOSTS or built-in defaults.
            check_hostname: Whether to check the current system's hostname
            check_targets: Whether to check targets in stage configuration
        """
        # Load from environment or use provided/default patterns
        if prohibited_patterns is not None:
            self.prohibited_patterns = set(prohibited_patterns)
        else:
            env_patterns = os.getenv("PROHIBITED_HOSTS", "")
            if env_patterns:
                self.prohibited_patterns = set(p.strip() for p in env_patterns.split(","))
            else:
                self.prohibited_patterns = self.DEFAULT_PROHIBITED.copy()

        self.check_hostname = check_hostname
        self.check_targets = check_targets

    def allow(self, stage: Any) -> bool:
        """
        Check if the stage targets production systems.

        From Listing 3.5 pattern:
            if "prod" in target:
                print("[Gate] Production system detected. Skipping.")
                return None

        Args:
            stage: The pipeline stage requesting permission

        Returns:
            True if no prohibited patterns found, False otherwise
        """
        stage_name = getattr(stage, "name", str(stage))

        # Check current hostname if enabled
        if self.check_hostname:
            import socket
            hostname = socket.gethostname().lower()
            for pattern in self.prohibited_patterns:
                if pattern.lower() in hostname:
                    print(
                        f"[EnvironmentGate] Blocked '{stage_name}': "
                        f"running on prohibited host '{hostname}'"
                    )
                    return False

        # Check stage targets if enabled
        if self.check_targets:
            targets = self._extract_targets(stage)
            for target in targets:
                target_lower = target.lower()
                for pattern in self.prohibited_patterns:
                    if pattern.lower() in target_lower:
                        print(
                            f"[EnvironmentGate] Blocked '{stage_name}': "
                            f"target '{target}' matches prohibited pattern '{pattern}'"
                        )
                        return False

        return True

    def _extract_targets(self, stage: Any) -> List[str]:
        """Extract target information from a stage."""
        targets = []

        # Check common target attributes
        for attr in ("target", "targets", "host", "hosts", "url", "urls"):
            if hasattr(stage, attr):
                value = getattr(stage, attr)
                if isinstance(value, list):
                    targets.extend(str(t) for t in value)
                elif value:
                    targets.append(str(value))

        # Check config dict
        if hasattr(stage, "config") and isinstance(stage.config, dict):
            for key in ("target", "targets", "host", "hosts"):
                if key in stage.config:
                    value = stage.config[key]
                    if isinstance(value, list):
                        targets.extend(str(t) for t in value)
                    elif value:
                        targets.append(str(value))

        return targets

    def __repr__(self) -> str:
        return f"EnvironmentGate(prohibited_patterns={list(self.prohibited_patterns)})"
