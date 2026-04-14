"""
Base Tool interface for AI agents.

From Listing 2.2 in Black Hat AI.

This module defines the abstract Tool class that all concrete tools must implement.
Tools provide capabilities that agents can invoke during execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """
    Abstract base class for agent tools.

    All tools must implement the invoke method to provide their functionality.
    Tools are discovered by agents through their name and description attributes.

    Example:
        class MyTool(Tool):
            def __init__(self):
                super().__init__(name="my_tool", description="Does something useful")

            def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "success"}
    """

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given input.

        Args:
            input: Dictionary containing tool-specific parameters

        Returns:
            Dictionary containing structured output from the tool
        """
        ...
