"""
AutoGen framework adapter.

Provides AutoGen-specific agent builders and configurations.
"""

from .agent import build_autogen_agent

__all__ = [
    "build_autogen_agent",
]
