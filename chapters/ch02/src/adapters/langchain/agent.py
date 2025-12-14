"""
LangChain agent adapter with artifact logging.

From Listing 2.6 in Black Hat AI.

Provides a factory function for creating LangChain agents with:
- OpenAI LLM backend
- Conversation memory
- Automatic artifact logging
- Tool integration
"""

import os
from typing import List, Callable
from ...core.logger import ArtifactLogger

# Conditional imports for optional LangChain support
try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.memory import ConversationBufferMemory
    from langchain_openai import ChatOpenAI
    from langchain.tools import Tool

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    Tool = None  # Type hint placeholder


def build_langchain_agent(tools: List[Tool]) -> Callable[[str], str]:
    """
    Build a LangChain agent with logging and memory.

    Creates a zero-shot ReAct agent that:
    - Uses OpenAI's LLM for reasoning
    - Maintains conversation history in memory
    - Logs all interactions to artifact files
    - Has access to provided tools

    Args:
        tools: List of LangChain Tool objects to provide to the agent

    Returns:
        Callable function that takes user input and returns agent response

    Raises:
        ImportError: If LangChain is not installed
        ValueError: If OPENAI_API_KEY environment variable is not set

    Example:
        from src.adapters.langchain.tools import ping_host_tool

        agent_run = build_langchain_agent([ping_host_tool])
        result = agent_run("Check if example.com is reachable")
        print(result)

    Note:
        Requires OPENAI_API_KEY environment variable to be set.
        Temperature is set to 0.2 for more deterministic responses.
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is not installed. Install with: pip install langchain langchain-openai"
        )

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it or copy .env.example to .env and configure."
        )

    # Initialize LLM with low temperature for reliability
    llm = ChatOpenAI(temperature=0.2)

    # Set up conversation memory
    memory = ConversationBufferMemory(memory_key="chat_history")

    # Create the agent
    agent = initialize_agent(
        tools,
        llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
    )

    # Initialize artifact logger
    logger = ArtifactLogger()

    def run(input_text: str) -> str:
        """
        Execute the agent with logging.

        Args:
            input_text: User's natural language request

        Returns:
            Agent's response as a string
        """
        result = agent.run(input_text)
        logger.write({"input": input_text, "output": result})
        return result

    return run
