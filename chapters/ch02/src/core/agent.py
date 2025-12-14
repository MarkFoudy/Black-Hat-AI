"""
Agent interface defining the plan-act-reflect cycle.

From Listing 2.4 in Black Hat AI.

This module defines the abstract Agent class that implements the core
reasoning loop used by AI agents: planning, acting, and reflecting.
"""

from typing import List, Optional
from .models import Message, Observation
from .tool import Tool


class Agent:
    """
    Abstract base class for AI agents using the plan-act-reflect pattern.

    The agent lifecycle consists of three phases:
    1. Plan: Analyze conversation history and decide next action
    2. Act: Execute the planned action using available tools
    3. Reflect: Process the observation and update internal state

    Subclasses should implement these methods to create functional agents.

    Example:
        class MyAgent(Agent):
            def plan(self, history: List[Message]) -> Message:
                # Analyze history and generate next action
                return Message(role="agent", content="...")

            def act(self, plan: Message, tools: List[Tool]) -> Observation:
                # Execute the planned action
                return Observation(...)

            def reflect(self, observation: Observation) -> Message:
                # Process results and produce reflection
                return Message(role="agent", content="...")
    """

    def plan(self, history: List[Message]) -> Optional[Message]:
        """
        Generate the next action or reasoning step.

        Analyzes the conversation history to determine what the agent
        should do next. This might involve:
        - Deciding which tool to use
        - Generating a reasoning step
        - Formulating a response to the user

        Args:
            history: Complete conversation history up to this point

        Returns:
            Message containing the planned action, or None if no action needed

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the plan() method"
        )

    def act(self, plan: Message, tools: List[Tool]) -> Optional[Observation]:
        """
        Execute the planned action using an appropriate tool.

        Takes the plan generated in the previous step and executes it
        by selecting and invoking the appropriate tool from the available set.

        Args:
            plan: The planned action (from the plan() method)
            tools: List of available tools the agent can use

        Returns:
            Observation containing the execution results, or None if no action taken

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the act() method"
        )

    def reflect(self, observation: Observation) -> Optional[Message]:
        """
        Update internal memory and produce a reflection message.

        Processes the observation from the action step, updating any
        internal state (memory, knowledge base) and generating a message
        that captures what was learned.

        Args:
            observation: The result from the act() method

        Returns:
            Message containing the agent's reflection, or None

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the reflect() method"
        )
