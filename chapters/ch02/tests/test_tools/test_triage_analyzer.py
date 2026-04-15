"""
Tests for TriageAnalyzerTool.

From Section 2.6 in Black Hat AI Chapter 2.
"""

import pytest
from src.tools.triage_analyzer import TriageAnalyzerTool


class TestTriageAnalyzerTool:
    """Test cases for triage analyzer tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = TriageAnalyzerTool()

    def test_tool_name(self):
        """Verify tool has correct name."""
        assert self.tool.name == "analyze_triage"

    def test_analyze_empty_hosts(self):
        """Test analysis of empty host list."""
        result = self.tool.invoke({"hosts": []})

        assert result["high_priority"] == []
        assert result["medium_priority"] == []
        assert result["low_priority"] == []
        assert result["summary"]["total_hosts"] == 0

    def test_detect_telnet_as_high_priority(self):
        """Test that telnet is flagged as high priority."""
        hosts = [{
            "hostname": "legacy.example.com",
            "services": [
                {"port": 23, "proto": "tcp", "state": "open", "service": "telnet", "version": ""}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        assert len(result["high_priority"]) == 1
        assert result["summary"]["high_count"] == 1
        host = result["high_priority"][0]
        assert host["hostname"] == "legacy.example.com"
        assert host["priority"] == "high"
        assert any(f["type"] == "legacy_service" for f in host["findings"])

    def test_detect_ftp_as_high_priority(self):
        """Test that FTP is flagged as high priority."""
        hosts = [{
            "hostname": "files.example.com",
            "services": [
                {"port": 21, "proto": "tcp", "state": "open", "service": "ftp", "version": "vsftpd 3.0.3"}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        assert len(result["high_priority"]) == 1
        finding = result["high_priority"][0]["findings"][0]
        assert finding["type"] == "legacy_service"
        assert finding["service"] == "ftp"

    def test_detect_eol_apache(self):
        """Test detection of end-of-life Apache versions."""
        hosts = [{
            "hostname": "old.example.com",
            "services": [
                {"port": 80, "proto": "tcp", "state": "open",
                 "service": "http", "version": "Apache httpd 2.2.34"}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        assert len(result["high_priority"]) == 1
        findings = result["high_priority"][0]["findings"]
        assert any(f["type"] == "eol_software" for f in findings)

    def test_detect_non_standard_port(self):
        """Test detection of non-standard ports."""
        hosts = [{
            "hostname": "api.example.com",
            "services": [
                {"port": 8443, "proto": "tcp", "state": "open",
                 "service": "https", "version": "Jetty 9.4.18"}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        assert len(result["medium_priority"]) == 1
        findings = result["medium_priority"][0]["findings"]
        assert any(f["type"] == "non_standard_port" for f in findings)
        assert any(f["port"] == 8443 for f in findings)

    def test_detect_odd_combination_ftp_http(self):
        """Test detection of FTP + HTTP combination."""
        hosts = [{
            "hostname": "mixed.example.com",
            "services": [
                {"port": 21, "proto": "tcp", "state": "open", "service": "ftp", "version": ""},
                {"port": 80, "proto": "tcp", "state": "open", "service": "http", "version": "nginx"}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        # Should be high due to FTP legacy service
        assert len(result["high_priority"]) == 1
        findings = result["high_priority"][0]["findings"]
        # Should have both legacy service and odd combination findings
        assert any(f["type"] == "legacy_service" for f in findings)
        assert any(f["type"] == "odd_combination" for f in findings)

    def test_low_priority_standard_services(self):
        """Test that standard services are marked as low priority."""
        hosts = [{
            "hostname": "web.example.com",
            "services": [
                {"port": 22, "proto": "tcp", "state": "open",
                 "service": "ssh", "version": "OpenSSH 8.2p1"},
                {"port": 443, "proto": "tcp", "state": "open",
                 "service": "https", "version": "nginx 1.18.0"}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        assert len(result["low_priority"]) == 1
        assert result["summary"]["low_count"] == 1

    def test_priority_counts_match(self):
        """Test that summary counts match actual results."""
        hosts = [
            {"hostname": "high1.com", "services": [
                {"port": 23, "proto": "tcp", "state": "open", "service": "telnet", "version": ""}
            ]},
            {"hostname": "medium1.com", "services": [
                {"port": 8443, "proto": "tcp", "state": "open", "service": "https", "version": ""}
            ]},
            {"hostname": "low1.com", "services": [
                {"port": 443, "proto": "tcp", "state": "open", "service": "https", "version": "nginx"}
            ]}
        ]

        result = self.tool.invoke({"hosts": hosts})

        assert result["summary"]["total_hosts"] == 3
        assert result["summary"]["high_count"] == len(result["high_priority"])
        assert result["summary"]["medium_count"] == len(result["medium_priority"])
        assert result["summary"]["low_count"] == len(result["low_priority"])

    def test_scoring_determines_priority(self):
        """Test that score correctly determines priority level."""
        # Create host with moderate score (should be medium)
        hosts = [{
            "hostname": "test.example.com",
            "services": [
                {"port": 8080, "proto": "tcp", "state": "open", "service": "http", "version": ""}
            ]
        }]

        result = self.tool.invoke({"hosts": hosts})

        # Non-standard port should give medium priority
        assert len(result["medium_priority"]) == 1
        assert result["medium_priority"][0]["score"] >= 15
        assert result["medium_priority"][0]["score"] < 40
