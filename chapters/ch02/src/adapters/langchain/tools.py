"""
LangChain-compatible tool wrappers.

From Listing 2.7 in Black Hat AI.

Provides LangChain-specific decorators and wrappers for tools,
allowing them to be used with LangChain agents.
"""

import subprocess


def ping_host(host: str) -> str:
    """
    Checks if a host responds to ICMP ping.

    This is a LangChain-compatible tool that returns a human-readable
    string message rather than structured data.

    Args:
        host: Target hostname or IP address

    Returns:
        Human-readable string describing reachability

    Note:
        To use with LangChain agents, wrap with @tool decorator:
        ```python
        from langchain.tools import tool

        @tool("ping_host", return_direct=True)
        def ping_host(host: str) -> str:
            # Implementation here
        ```

    Example:
        result = ping_host("example.com")
        # Returns: "example.com is reachable." or "example.com did not respond."
    """
    try:
        subprocess.check_output(["ping", "-c", "1", host], timeout=3)
        return f"{host} is reachable."
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return f"{host} did not respond."


# LangChain decorated version (optional - requires langchain installed)
try:
    from langchain.tools import tool

    # Create LangChain-decorated version
    ping_host_tool = tool("ping_host", return_direct=True)(ping_host)

except ImportError:
    # LangChain not installed - skip decorator
    ping_host_tool = None
