"""
Scope gate for authorized target filtering.

From Table 3.4 in Black Hat AI.

Prevents agents from acting outside authorized targets.
"""

import json
import os
from typing import Any, List, Optional, Set

from .base import BaseGate


class ScopeGate(BaseGate):
    """
    Gate that ensures operations stay within authorized scope.

    This gate checks that targets are in an authorized list and
    don't match any excluded patterns. Critical for:
    - Staying within client engagement boundaries
    - Preventing accidental scans of production systems
    - Documenting scope compliance for audits

    Attributes:
        authorized_domains: Set of allowed domain patterns
        excluded_patterns: Set of patterns that are never allowed

    Example:
        gate = ScopeGate(
            authorized_domains=["example.com", "test.local"],
            excluded_patterns=["prod", "payment"]
        )
    """

    def __init__(
        self,
        authorized_domains: Optional[List[str]] = None,
        excluded_patterns: Optional[List[str]] = None,
        scope_file: Optional[str] = None,
    ):
        """
        Initialize the scope gate.

        Args:
            authorized_domains: List of authorized domain patterns
            excluded_patterns: List of patterns to always exclude
            scope_file: Path to JSON file with scope configuration
        """
        self.authorized_domains: Set[str] = set(authorized_domains or [])
        self.excluded_patterns: Set[str] = set(excluded_patterns or [])

        # Load from file if provided
        if scope_file and os.path.exists(scope_file):
            self._load_scope_file(scope_file)

    def _load_scope_file(self, path: str) -> None:
        """Load scope configuration from JSON file."""
        with open(path, "r") as f:
            config = json.load(f)
            if "authorized_domains" in config:
                self.authorized_domains.update(config["authorized_domains"])
            if "excluded_patterns" in config:
                self.excluded_patterns.update(config["excluded_patterns"])

    def allow(self, stage: Any) -> bool:
        """
        Check if the stage's targets are within scope.

        Args:
            stage: Pipeline stage to check

        Returns:
            True if stage targets are within scope
        """
        # Get targets from stage if available
        targets = self._extract_targets(stage)

        if not targets:
            # No targets to check, allow by default
            return True

        for target in targets:
            # Check excluded patterns first
            if any(pattern in target for pattern in self.excluded_patterns):
                print(f"[ScopeGate] Blocked: '{target}' matches excluded pattern")
                return False

            # Check if target is in authorized domains
            if self.authorized_domains:
                if not any(domain in target for domain in self.authorized_domains):
                    print(f"[ScopeGate] Blocked: '{target}' not in authorized domains")
                    return False

        return True

    def _extract_targets(self, stage: Any) -> List[str]:
        """
        Extract target information from a stage.

        Looks for common attributes that might contain targets.
        """
        targets = []

        # Check for targets attribute
        if hasattr(stage, "targets"):
            targets.extend(stage.targets if isinstance(stage.targets, list) else [stage.targets])

        # Check for target attribute
        if hasattr(stage, "target"):
            targets.append(stage.target)

        # Check for config with targets
        if hasattr(stage, "config") and isinstance(stage.config, dict):
            if "targets" in stage.config:
                t = stage.config["targets"]
                targets.extend(t if isinstance(t, list) else [t])
            if "target" in stage.config:
                targets.append(stage.config["target"])

        return targets

    def __repr__(self) -> str:
        return (
            f"ScopeGate(authorized_domains={list(self.authorized_domains)}, "
            f"excluded_patterns={list(self.excluded_patterns)})"
        )
