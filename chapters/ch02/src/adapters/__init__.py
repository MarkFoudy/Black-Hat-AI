"""
Framework adapters for AI agent libraries.

Provides adapters for:
- LangChain
- AutoGen
- Universal selector for switching between frameworks
"""

from .selector import get_agent

__all__ = [
    "get_agent",
]
