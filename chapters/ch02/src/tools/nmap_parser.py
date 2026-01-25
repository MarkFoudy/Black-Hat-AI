"""
NMAP output parser tool.

From Section 2.6 in Black Hat AI Chapter 2.

Parses simplified nmap scan output into structured data for analysis.
Supports the human-readable format shown in the chapter examples.
"""

import re
from typing import Dict, Any, List

from src.core.tool import Tool


class NmapParserTool(Tool):
    """Parse simplified nmap output into structured data."""

    name = "parse_nmap"
    description = "Parse nmap scan output into structured host/service data"

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse nmap text output into structured format.

        Expected input format (from Listing 2.11):
            Host: api.example.com
              80/tcp    open  http    Apache httpd 2.4.41
              443/tcp   open  https   Apache httpd 2.4.41

        Args:
            input: Dictionary with "text" key containing nmap output

        Returns:
            Dictionary with "hosts" key containing list of host objects:
            {
                "hosts": [
                    {
                        "hostname": "api.example.com",
                        "services": [
                            {
                                "port": 80,
                                "proto": "tcp",
                                "state": "open",
                                "service": "http",
                                "version": "Apache httpd 2.4.41"
                            }
                        ]
                    }
                ]
            }
        """
        text = input.get("text", "")
        hosts = []
        current_host = None

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check for host line
            if line.startswith("Host:"):
                # Save previous host if exists
                if current_host:
                    hosts.append(current_host)

                # Start new host
                hostname = line.replace("Host:", "").strip()
                current_host = {
                    "hostname": hostname,
                    "services": []
                }

            # Check for service line
            elif current_host and "/" in line:
                # Parse service line: "80/tcp    open  http    Apache httpd 2.4.41"
                parts = line.split(None, 4)  # Split on whitespace, max 5 parts

                if len(parts) >= 4:
                    # Parse port/protocol
                    port_proto = parts[0].split("/")
                    port = int(port_proto[0]) if port_proto[0].isdigit() else 0
                    proto = port_proto[1] if len(port_proto) > 1 else "tcp"

                    state = parts[1]
                    service = parts[2]
                    version = parts[3] if len(parts) > 3 else ""

                    # Add remaining parts to version if they exist
                    if len(parts) > 4:
                        version = parts[3] + " " + parts[4]

                    current_host["services"].append({
                        "port": port,
                        "proto": proto,
                        "state": state,
                        "service": service,
                        "version": version.strip()
                    })

        # Don't forget the last host
        if current_host:
            hosts.append(current_host)

        return {"hosts": hosts}
