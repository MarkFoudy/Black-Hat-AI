"""
LLM framework adapters for multi-agent pipelines.

This module provides adapter interfaces for integrating with LLM frameworks
like LangChain, keeping orchestration logic framework-agnostic.
"""

from .base import LLMAdapter

__all__ = ["LLMAdapter"]

# Conditional imports for optional dependencies
try:
    from .langchain import LangChainAdapter
    __all__.append("LangChainAdapter")
except ImportError:
    pass
