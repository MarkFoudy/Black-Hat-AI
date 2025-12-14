"""
Network reachability testing tool.

From Listing 2.3 in Black Hat AI.

Provides ICMP ping functionality for testing host reachability.
Useful for reconnaissance and infrastructure mapping.
"""

import subprocess
from typing import Dict, Any
from ..core.tool import Tool


class PingTool(Tool):
    """
    Tool for checking if a host is reachable via ICMP ping.

    This tool executes a single ping packet to test network connectivity.
    It's useful for:
    - Verifying host is online
    - Testing network connectivity
    - Basic reconnaissance

    Note:
        - Requires ICMP to be allowed (may be blocked by firewalls)
        - Uses system ping command (platform-specific)
        - Timeout set to 3 seconds for responsive testing

    Example:
        tool = PingTool()
        result = tool.invoke({"host": "example.com"})
        # Returns: {"reachable": True} or {"reachable": False}
    """

    name = "ping"
    description = "Checks if a host is reachable."

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ping a target host to check if it's alive and reachable.

        Args:
            input: Dict with "host" (str) - target IP or hostname

        Returns:
            Dict with "reachable" (bool) - True if host responds

        Note:
            May return False if ICMP is blocked by firewall.
        """
        host = input["host"]
        try:
            subprocess.check_output(["ping", "-c", "1", host], timeout=3)
            return {"reachable": True}
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return {"reachable": False}


# Functional interface for backward compatibility and convenience
def ping_host(host: str) -> Dict[str, Any]:
    """
    Convenience function for pinging a host.

    Args:
        host: Target hostname or IP address

    Returns:
        Dictionary with reachability result

    Example:
        result = ping_host("example.com")
        print(result["reachable"])  # True or False
    """
    tool = PingTool()
    return tool.invoke({"host": host})
