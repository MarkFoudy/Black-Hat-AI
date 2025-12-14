from langchain.tools import tool
import subprocess

# Tells LangChain this is a tool
@tool("ping_host", return_direct=True)
def ping_host(host: str) -> str:
    """Checks if a host responds to ICMP ping."""
    try:
        subprocess.check_output(["ping", "-c", "1", host], timeout=3)
        return f"{host} is reachable."
    except subprocess.CalledProcessError:
        return f"{host} did not respond."
