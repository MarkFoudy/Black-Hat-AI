"""
Base adapter interface for LLM frameworks.

Provides an abstract interface that allows the orchestrator to remain
framework-agnostic while supporting multiple LLM backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMAdapter(ABC):
    """
    Abstract base class for LLM framework adapters.

    Adapters translate between the orchestrator's interface and
    specific LLM frameworks (LangChain, AutoGen, etc.).

    This keeps the orchestrator logic independent of any particular
    framework, making it easy to swap implementations.

    Example:
        class MyAdapter(LLMAdapter):
            def invoke(self, prompt, context=None):
                # Call your LLM
                return response
    """

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Invoke the LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM
            context: Optional context dictionary

        Returns:
            LLM response as a string
        """
        pass

    @abstractmethod
    def invoke_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke the LLM with tool-calling capability.

        Args:
            prompt: The prompt to send
            tools: List of tool definitions
            context: Optional context

        Returns:
            Dictionary with response and any tool calls
        """
        pass

    def is_available(self) -> bool:
        """Check if this adapter is properly configured and available."""
        return True
