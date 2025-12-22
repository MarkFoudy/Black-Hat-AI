"""
Scope Enforcement Module (Section 4.6)

Provides scope configuration and enforcement for reconnaissance operations.
Ensures agents operate within authorized boundaries.

The difference between authorized reconnaissance and illegal scanning
is not technical; it's ethical. This module helps enforce those boundaries.
"""

import fnmatch
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.core.artifacts import ScopeArtifact, write_jsonl


@dataclass
class ScopeConfig:
    """
    Configuration defining allowed and forbidden targets.

    Attributes:
        allowed: List of domain patterns that ARE permitted
        forbidden: List of domain patterns that are NEVER permitted
                  (takes precedence over allowed)

    Patterns support wildcards:
        - "example.com" matches exactly "example.com"
        - "*.example.com" matches any subdomain of example.com
        - "prod.*" matches any domain starting with "prod."
    """

    allowed: List[str] = field(default_factory=list)
    forbidden: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "allowed": self.allowed,
            "forbidden": self.forbidden,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScopeConfig":
        """Create from dictionary."""
        return cls(
            allowed=data.get("allowed", []),
            forbidden=data.get("forbidden", []),
        )


class ScopeChecker:
    """
    Checks whether hosts are within the authorized scope.

    Example:
        >>> config = ScopeConfig(
        ...     allowed=["example.com", "*.example.com"],
        ...     forbidden=["prod.example.com"]
        ... )
        >>> checker = ScopeChecker(config)
        >>> checker.is_allowed("dev.example.com")
        (True, 'matches allowed pattern: *.example.com')
        >>> checker.is_allowed("prod.example.com")
        (False, 'matches forbidden pattern: prod.example.com')
    """

    def __init__(self, config: ScopeConfig):
        """
        Initialize the scope checker.

        Args:
            config: ScopeConfig defining allowed/forbidden patterns
        """
        self.config = config

    def _matches_pattern(self, host: str, pattern: str) -> bool:
        """
        Check if host matches a pattern (supports wildcards).

        Args:
            host: Hostname to check
            pattern: Pattern to match against (supports * wildcards)

        Returns:
            True if host matches pattern
        """
        # Normalize both to lowercase
        host = host.lower()
        pattern = pattern.lower()

        # Use fnmatch for glob-style matching
        return fnmatch.fnmatch(host, pattern)

    def is_allowed(self, host: str) -> Tuple[bool, str]:
        """
        Check if a host is within scope.

        Forbidden patterns take precedence over allowed patterns.

        Args:
            host: Hostname to check

        Returns:
            Tuple of (is_allowed, reason)
            - is_allowed: True if host is in scope
            - reason: Human-readable explanation
        """
        host = host.lower()

        # Check forbidden patterns first (they take precedence)
        for pattern in self.config.forbidden:
            if self._matches_pattern(host, pattern):
                return False, f"matches forbidden pattern: {pattern}"

        # If no allowed patterns, everything (not forbidden) is allowed
        if not self.config.allowed:
            return True, "no allowed patterns defined, default allow"

        # Check allowed patterns
        for pattern in self.config.allowed:
            if self._matches_pattern(host, pattern):
                return True, f"matches allowed pattern: {pattern}"

        # Not in allowed list
        return False, "does not match any allowed pattern"

    def check_and_log(
        self,
        host: str,
        artifact_path: Optional[str] = None,
    ) -> bool:
        """
        Check scope and log the decision as an artifact.

        Args:
            host: Hostname to check
            artifact_path: Path for artifact logging (optional)

        Returns:
            True if host is allowed
        """
        allowed, reason = self.is_allowed(host)

        # Log the decision as a scope artifact
        if artifact_path:
            artifact = ScopeArtifact(
                host=host,
                action="allowed" if allowed else "blocked",
                reason=reason,
            )
            write_jsonl(artifact, artifact_path)

        return allowed

    def filter_hosts(self, hosts: List[str]) -> Tuple[List[str], List[str]]:
        """
        Filter a list of hosts by scope.

        Args:
            hosts: List of hostnames to check

        Returns:
            Tuple of (allowed_hosts, blocked_hosts)
        """
        allowed_hosts = []
        blocked_hosts = []

        for host in hosts:
            is_allowed, _ = self.is_allowed(host)
            if is_allowed:
                allowed_hosts.append(host)
            else:
                blocked_hosts.append(host)

        return allowed_hosts, blocked_hosts


def load_scope(path: str = "data/scope.json") -> ScopeConfig:
    """
    Load scope configuration from a JSON file.

    Args:
        path: Path to scope.json file

    Returns:
        ScopeConfig instance

    Raises:
        FileNotFoundError: If scope file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return ScopeConfig.from_dict(data)


def load_scope_safe(path: str = "data/scope.json") -> Optional[ScopeConfig]:
    """
    Load scope configuration, returning None if file doesn't exist.

    Args:
        path: Path to scope.json file

    Returns:
        ScopeConfig instance or None if file not found
    """
    if not os.path.exists(path):
        return None

    try:
        return load_scope(path)
    except (json.JSONDecodeError, KeyError):
        return None


def save_scope(config: ScopeConfig, path: str = "data/scope.json") -> None:
    """
    Save scope configuration to a JSON file.

    Args:
        config: ScopeConfig to save
        path: Output file path
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)
        f.write("\n")


def create_scope_checker(
    allowed: Optional[List[str]] = None,
    forbidden: Optional[List[str]] = None,
    config_path: Optional[str] = None,
) -> ScopeChecker:
    """
    Create a ScopeChecker from arguments or config file.

    Priority:
    1. Explicit allowed/forbidden lists
    2. Config file path
    3. Default config path (data/scope.json)
    4. Empty config (allow all)

    Args:
        allowed: List of allowed patterns
        forbidden: List of forbidden patterns
        config_path: Path to scope.json file

    Returns:
        Configured ScopeChecker instance
    """
    if allowed is not None or forbidden is not None:
        config = ScopeConfig(
            allowed=allowed or [],
            forbidden=forbidden or [],
        )
    elif config_path:
        config = load_scope(config_path)
    else:
        config = load_scope_safe() or ScopeConfig()

    return ScopeChecker(config)
