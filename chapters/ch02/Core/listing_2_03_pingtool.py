import subprocess, json


class PingTool(Tool):
    name = "ping"
    description = "Checks if a host is reachable."

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
    Ping a target host to check if it's alive and reachable.

    Args:
 input: Dict with "host" (str) - target IP or hostname

 Returns:
 Dict with "reachable" (bool) - True if host responds

 Note: May return False if ICMP is blocked by firewall.
 """

    host = input["host"]
    try:
        subprocess.check_output(["ping", "-c", "1", host], timeout=3)
        return {"reachable": True}
    except subprocess.CalledProcessError:
        return {"reachable": False}
