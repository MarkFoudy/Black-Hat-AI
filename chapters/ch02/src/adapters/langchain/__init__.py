"""
LangChain framework adapter.

Provides LangChain-specific agent builders and tool wrappers.
"""

from .agent import build_langchain_agent
from .tools import ping_host

__all__ = [
    "build_langchain_agent",
    "ping_host",
]
