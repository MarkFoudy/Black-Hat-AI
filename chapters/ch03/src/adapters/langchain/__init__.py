"""
LangChain adapter for multi-agent pipelines.

Provides LangChain integration for orchestrated pipelines.
"""

try:
    from .agent import LangChainAdapter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LangChainAdapter = None

__all__ = ["LangChainAdapter", "LANGCHAIN_AVAILABLE"]
