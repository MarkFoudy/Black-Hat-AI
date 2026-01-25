"""
Triage analysis tool for prioritizing reconnaissance targets.

From Section 2.6 in Black Hat AI Chapter 2.

Analyzes parsed nmap data and assigns priority scores based on:
- Unusual service exposure (telnet, FTP, non-standard ports)
- End-of-life software versions
- Odd service combinations
- Potential admin/management interfaces
"""

from typing import Dict, Any, List

from src.core.tool import Tool


class TriageAnalyzerTool(Tool):
    """Analyze parsed nmap data and prioritize targets."""

    name = "analyze_triage"
    description = "Prioritize reconnaissance targets based on risk indicators"

    # Risk indicators from Section 2.6.3
    LEGACY_SERVICES = {
        "telnet": "Unencrypted remote access",
        "ftp": "Unencrypted file transfer",
        "rsh": "Unencrypted remote shell",
        "rlogin": "Unencrypted remote login"
    }

    NON_STANDARD_PORTS = {
        8080, 8443, 8000, 8888, 9000, 9090, 4443, 8008
    }

    EOL_SOFTWARE = {
        "Apache httpd 2.2": "End-of-life Apache version",
        "OpenSSH 6.": "Outdated SSH version",
        "OpenSSH 5.": "Critically outdated SSH version",
    }

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze hosts and assign priority scores.

        Args:
            input: Dictionary with "hosts" key from NmapParserTool

        Returns:
            Dictionary with prioritized findings:
            {
                "high_priority": [...],
                "medium_priority": [...],
                "low_priority": [...],
                "summary": {...}
            }
        """
        hosts = input.get("hosts", [])
        results = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "summary": {
                "total_hosts": len(hosts),
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0
            }
        }

        for host in hosts:
            analysis = self._analyze_host(host)
            priority = analysis["priority"]

            if priority == "high":
                results["high_priority"].append(analysis)
                results["summary"]["high_count"] += 1
            elif priority == "medium":
                results["medium_priority"].append(analysis)
                results["summary"]["medium_count"] += 1
            else:
                results["low_priority"].append(analysis)
                results["summary"]["low_count"] += 1

        return results

    def _analyze_host(self, host: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single host and assign priority.

        Returns analysis dict with:
        - hostname
        - priority: "high", "medium", or "low"
        - score: numeric score for sorting
        - findings: list of specific issues found
        - services: summary of services
        """
        hostname = host.get("hostname", "unknown")
        services = host.get("services", [])

        findings = []
        score = 0

        # Check for legacy services (HIGH priority)
        for service in services:
            service_name = service.get("service", "").lower()
            if service_name in self.LEGACY_SERVICES:
                findings.append({
                    "type": "legacy_service",
                    "severity": "high",
                    "port": service["port"],
                    "service": service_name,
                    "reason": self.LEGACY_SERVICES[service_name]
                })
                score += 50

        # Check for end-of-life software (HIGH priority)
        for service in services:
            version = service.get("version", "")
            for eol_pattern, reason in self.EOL_SOFTWARE.items():
                if eol_pattern in version:
                    findings.append({
                        "type": "eol_software",
                        "severity": "high",
                        "port": service["port"],
                        "version": version,
                        "reason": reason
                    })
                    score += 40

        # Check for non-standard ports (MEDIUM priority)
        for service in services:
            port = service.get("port", 0)
            if port in self.NON_STANDARD_PORTS:
                findings.append({
                    "type": "non_standard_port",
                    "severity": "medium",
                    "port": port,
                    "service": service.get("service", ""),
                    "reason": "Non-standard port may indicate admin/management interface"
                })
                score += 20

        # Check for odd combinations (MEDIUM priority)
        service_names = [s.get("service", "").lower() for s in services]
        if "ftp" in service_names and ("http" in service_names or "https" in service_names):
            findings.append({
                "type": "odd_combination",
                "severity": "medium",
                "reason": "FTP exposed alongside web server"
            })
            score += 25

        # Determine overall priority
        if score >= 40:
            priority = "high"
        elif score >= 15:
            priority = "medium"
        else:
            priority = "low"

        return {
            "hostname": hostname,
            "priority": priority,
            "score": score,
            "findings": findings,
            "services": services,
            "service_count": len(services)
        }
