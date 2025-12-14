"""
Base Tool interface for AI agents.

From Listing 2.2 in Black Hat AI.

This module defines the abstract Tool class that all concrete tools must implement.
Tools provide capabilities that agents can invoke during execution.
"""

from typing import Dict, Any


class Tool:
    """
    Abstract base class for agent tools.

    All tools must implement the invoke method to provide their functionality.
    Tools are discovered by agents through their name and description attributes.

    Attributes:
        name: Unique identifier for the tool (used in agent prompts)
        description: Natural language description of what the tool does
                    (helps LLM decide when to use it)

    Example:
        class MyTool(Tool):
            name = "my_tool"
            description = "Does something useful"

            def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "success"}
    """

    name: str
    description: str

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given input.

        Args:
            input: Dictionary containing tool-specific parameters

        Returns:
            Dictionary containing structured output from the tool

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the invoke() method"
        )
