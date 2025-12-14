"""
Universal adapter selector for switching between agent frameworks.

From Listing 2.13 in Black Hat AI.

Provides a unified interface for selecting between different agent frameworks
(LangChain, AutoGen, etc.) at runtime.
"""

from typing import Callable, Optional, List

# Import adapters with fallback if not available
try:
    from .langchain.agent import build_langchain_agent

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    build_langchain_agent = None

try:
    from .autogen.agent import build_autogen_agent

    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    build_autogen_agent = None


def get_agent(
    adapter: str = "langchain", tools: Optional[List] = None
) -> Callable[[str], str]:
    """
    Get an agent using the specified framework adapter.

    This function provides a unified interface for creating agents
    regardless of the underlying framework. Useful for:
    - A/B testing different frameworks
    - Switching frameworks without changing client code
    - Fallback to available frameworks

    Args:
        adapter: Framework to use ("langchain" or "autogen")
        tools: List of tools to provide to the agent (LangChain only)

    Returns:
        Callable agent function that takes a prompt string and returns response

    Raises:
        ValueError: If specified adapter is not available or unknown
        ImportError: If no adapters are available

    Example:
        # Use LangChain
        agent = get_agent(adapter="langchain", tools=[ping_tool])
        result = agent("Check if example.com is reachable")

        # Use AutoGen
        agent = get_agent(adapter="autogen")
        result = agent("Check if example.com is reachable")

    Note:
        - LangChain adapter requires tools to be passed
        - AutoGen adapter does not currently use the tools parameter
        - Both adapters require OPENAI_API_KEY environment variable
    """
    # Normalize adapter name
    adapter = adapter.lower().strip()

    if adapter == "autogen":
        if not AUTOGEN_AVAILABLE or build_autogen_agent is None:
            raise ValueError(
                "AutoGen adapter not available. Install with: pip install pyautogen"
            )
        return build_autogen_agent()

    elif adapter == "langchain":
        if not LANGCHAIN_AVAILABLE or build_langchain_agent is None:
            raise ValueError(
                "LangChain adapter not available. "
                "Install with: pip install langchain langchain-openai"
            )
        return build_langchain_agent(tools or [])

    else:
        raise ValueError(
            f"Unknown adapter: {adapter}. Available: 'langchain', 'autogen'"
        )


def list_available_adapters() -> List[str]:
    """
    List all available agent adapters.

    Returns:
        List of adapter names that can be used with get_agent()

    Example:
        adapters = list_available_adapters()
        print(f"Available adapters: {', '.join(adapters)}")
    """
    available = []
    if LANGCHAIN_AVAILABLE:
        available.append("langchain")
    if AUTOGEN_AVAILABLE:
        available.append("autogen")
    return available
