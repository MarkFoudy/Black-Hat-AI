"""
LangChain adapter for multi-agent pipeline integration.

Provides LangChain-based LLM invocation for pipeline stages.
"""

import os
from typing import List, Dict, Any, Optional

from ..base import LLMAdapter

# Conditional imports for optional LangChain support
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None


class LangChainAdapter(LLMAdapter):
    """
    LangChain-based LLM adapter.

    Uses LangChain's ChatOpenAI for LLM invocations. Provides a clean
    interface for the orchestrator while leveraging LangChain's capabilities.

    Attributes:
        llm: LangChain ChatOpenAI instance
        temperature: Temperature for LLM responses
        model: Model name

    Example:
        adapter = LangChainAdapter(model="gpt-4", temperature=0.2)
        response = adapter.invoke("Analyze these findings...")
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the LangChain adapter.

        Args:
            model: OpenAI model name
            temperature: Temperature for responses (0-1)
            api_key: Optional API key (uses env var if not provided)

        Raises:
            ImportError: If LangChain is not installed
            ValueError: If API key is not available
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. "
                "Install with: pip install langchain langchain-openai"
            )

        self.model = model
        self.temperature = temperature

        # Get API key
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OPENAI_API_KEY not set. "
                "Set the environment variable or pass api_key parameter."
            )

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=key,
        )

    def invoke(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Invoke the LLM with a prompt.

        Args:
            prompt: The prompt to send
            context: Optional context (added as system message)

        Returns:
            LLM response text
        """
        messages = []

        # Add context as system message if provided
        if context:
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
            messages.append(SystemMessage(content=f"Context:\n{context_str}"))

        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages)
        return response.content

    def invoke_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke the LLM with tool-calling capability.

        Note: This is a simplified implementation. For full tool-calling
        support, consider using LangChain's agent framework.

        Args:
            prompt: The prompt to send
            tools: List of tool definitions (not fully implemented)
            context: Optional context

        Returns:
            Dictionary with response text
        """
        # Simple implementation - just invoke without tools
        response = self.invoke(prompt, context)
        return {"response": response, "tool_calls": []}

    def is_available(self) -> bool:
        """Check if the adapter is properly configured."""
        return LANGCHAIN_AVAILABLE and self.llm is not None
