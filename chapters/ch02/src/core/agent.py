"""
MinimalAgent implementation.

From Listing 2.6 in Black Hat AI.

This module defines MinimalAgent, the smallest possible agent that still
exhibits core agent behaviors: orchestrating tools, recording observations,
and producing reproducible results — all without an AI framework.
"""

from typing import List
from .models import Message, Observation
from .tool import Tool


class MinimalAgent:
    """
    Minimal agent implementation without framework dependencies.

    From Listing 2.6 in Black Hat AI Chapter 2.

    This agent demonstrates the simplest possible agent: it runs two tools
    in sequence (extract URLs, then summarize them) without any LLM calls,
    memory, or complex orchestration. All decision-making is explicit and
    hardcoded.

    The purpose is educational: to show the mechanics of agent execution
    without framework abstractions obscuring the core concepts.

    Example:
        with ArtifactLogger() as logger:
            agent = MinimalAgent(
                tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
                logger=logger,
            )
            result = agent.run(
                "Check https://example.com and "
                "https://admin.example.com/login"
            )
            print(result)
    """

    def __init__(self, tools: List[Tool], logger) -> None:
        """
        Initialize the minimal agent.

        Args:
            tools: List of Tool instances to make available
            logger: ArtifactLogger instance for recording observations
        """
        self.tools = {tool.name: tool for tool in tools}
        self.logger = logger
        self.history: List[Message] = []

    def run(self, text: str):
        """
        Run the agent workflow on the provided text.

        This is a hardcoded two-step workflow:
        1. Extract URLs from the text
        2. Summarize the extracted URLs

        Every tool result is wrapped in an Observation and serialized with
        .model_dump(mode='json') before logging.

        Args:
            text: Input text to process

        Returns:
            Dictionary with "count", "summary", and "urls" keys
        """
        self.history.append(Message(role="user", content=text))

        # Step 1: Extract URLs
        try:
            step_1_output = self.tools["extract_urls"].invoke({"text": text})
            obs_1 = Observation(
                tool_name="extract_urls",
                input={"text": text},
                output=step_1_output,
                success=True,
            )
        except Exception as e:
            obs_1 = Observation(
                tool_name="extract_urls",
                input={"text": text},
                output={},
                success=False,
                error=str(e),
            )
            self.logger.write(obs_1.model_dump(mode="json"))
            raise

        self.logger.write(obs_1.model_dump(mode="json"))

        # Step 2: Summarize URLs
        try:
            step_2_output = self.tools["summarize_urls"].invoke(step_1_output)
            obs_2 = Observation(
                tool_name="summarize_urls",
                input=step_1_output,
                output=step_2_output,
                success=True,
            )
        except Exception as e:
            obs_2 = Observation(
                tool_name="summarize_urls",
                input=step_1_output,
                output={},
                success=False,
                error=str(e),
            )
            self.logger.write(obs_2.model_dump(mode="json"))
            raise

        self.logger.write(obs_2.model_dump(mode="json"))

        self.history.append(
            Message(
                role="agent",
                content=step_2_output["summary"],
                meta=step_2_output,
            )
        )

        return step_2_output
