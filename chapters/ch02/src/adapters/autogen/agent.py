"""
AutoGen agent adapter with artifact logging.

From Listing 2.12 in Black Hat AI.

Provides a factory function for creating AutoGen agents with:
- Multi-agent conversation (AssistantAgent + UserProxyAgent)
- Tool registration
- Automatic artifact logging
"""

import os
from typing import Callable
from ...core.logger import ArtifactLogger

# Conditional imports for optional AutoGen support
try:
    from autogen import AssistantAgent, UserProxyAgent

    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False


def build_autogen_agent() -> Callable[[str], str]:
    """
    Build an AutoGen multi-agent system with logging.

    Creates a pair of AutoGen agents:
    - AssistantAgent: AI-powered agent that reasons and plans
    - UserProxyAgent: Represents the user/operator (no code execution)

    The agents communicate to accomplish tasks, with all interactions
    logged to artifact files.

    Returns:
        Callable function that takes a prompt and initiates agent chat

    Raises:
        ImportError: If AutoGen is not installed
        ValueError: If OPENAI_API_KEY environment variable is not set

    Example:
        from src.tools.ping import ping_host

        agent_run = build_autogen_agent()
        # Note: Tool registration happens within the function
        result = agent_run("Check reachability of example.com")

    Note:
        Requires OPENAI_API_KEY environment variable to be set.
        Temperature is set to 0.2 for more deterministic responses.
        Code execution is disabled for security.
    """
    if not AUTOGEN_AVAILABLE:
        raise ImportError(
            "AutoGen is not installed. Install with: pip install pyautogen"
        )

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it or copy .env.example to .env and configure."
        )

    # Initialize artifact logger
    logger = ArtifactLogger()

    # Create assistant agent (AI-powered)
    assistant = AssistantAgent(
        name="triage",
        llm_config={"temperature": 0.2, "config_list": [{"model": "gpt-4"}]},
    )

    # Create user proxy agent (represents human operator)
    user = UserProxyAgent(
        name="operator",
        code_execution_config=False,  # Disable code execution for security
    )

    # Tool registration would happen here
    # assistant.register_function(ping_host)

    def run(prompt: str) -> str:
        """
        Execute the AutoGen agent system with logging.

        Args:
            prompt: User's natural language request

        Returns:
            Agent's response (conversation summary)
        """
        result = assistant.initiate_chat(user, message=prompt)
        logger.write({"input": prompt, "output": str(result)})
        return str(result)

    return run


# Entry point for standalone execution
if __name__ == "__main__":
    agent_run = build_autogen_agent()
    result = agent_run("Check reachability of example.com")
    print(result)
