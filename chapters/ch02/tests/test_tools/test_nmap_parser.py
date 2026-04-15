"""
Tests for NmapParserTool.

From Section 2.6 in Black Hat AI Chapter 2.
"""

import pytest
from src.tools.nmap_parser import NmapParserTool


class TestNmapParserTool:
    """Test cases for NMAP parser tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = NmapParserTool()

    def test_tool_name(self):
        """Verify tool has correct name."""
        assert self.tool.name == "parse_nmap"

    def test_parse_single_host(self):
        """Test parsing a single host with services."""
        nmap_output = """Host: example.com
  80/tcp    open  http    Apache httpd 2.4.41
  443/tcp   open  https   Apache httpd 2.4.41"""

        result = self.tool.invoke({"text": nmap_output})

        assert len(result["hosts"]) == 1
        host = result["hosts"][0]
        assert host["hostname"] == "example.com"
        assert len(host["services"]) == 2

        # Check first service
        assert host["services"][0]["port"] == 80
        assert host["services"][0]["proto"] == "tcp"
        assert host["services"][0]["state"] == "open"
        assert host["services"][0]["service"] == "http"
        assert "Apache" in host["services"][0]["version"]

    def test_parse_multiple_hosts(self):
        """Test parsing multiple hosts."""
        nmap_output = """Host: host1.com
  80/tcp    open  http    nginx
Host: host2.com
  22/tcp    open  ssh     OpenSSH"""

        result = self.tool.invoke({"text": nmap_output})

        assert len(result["hosts"]) == 2
        assert result["hosts"][0]["hostname"] == "host1.com"
        assert result["hosts"][1]["hostname"] == "host2.com"

    def test_parse_empty_input(self):
        """Test handling of empty input."""
        result = self.tool.invoke({"text": ""})
        assert result["hosts"] == []

    def test_parse_no_services(self):
        """Test host with no services listed."""
        nmap_output = "Host: example.com"
        result = self.tool.invoke({"text": nmap_output})

        assert len(result["hosts"]) == 1
        assert result["hosts"][0]["services"] == []

    def test_parse_telnet_service(self):
        """Test parsing telnet (service without version)."""
        nmap_output = """Host: legacy.example.com
  23/tcp    open  telnet"""

        result = self.tool.invoke({"text": nmap_output})

        assert len(result["hosts"]) == 1
        service = result["hosts"][0]["services"][0]
        assert service["port"] == 23
        assert service["service"] == "telnet"
        assert service["version"] == ""

    def test_parse_non_standard_port(self):
        """Test parsing non-standard ports like 8443."""
        nmap_output = """Host: api.example.com
  8443/tcp  open  https   Jetty 9.4.18"""

        result = self.tool.invoke({"text": nmap_output})

        service = result["hosts"][0]["services"][0]
        assert service["port"] == 8443
        assert service["service"] == "https"
        assert "Jetty" in service["version"]

    def test_parse_with_blank_lines(self):
        """Test parser handles blank lines correctly."""
        nmap_output = """Host: example.com

  80/tcp    open  http    nginx

Host: test.com
  22/tcp    open  ssh     OpenSSH"""

        result = self.tool.invoke({"text": nmap_output})
        assert len(result["hosts"]) == 2

    def test_parse_version_with_multiple_words(self):
        """Test parsing version strings with multiple words."""
        nmap_output = """Host: example.com
  80/tcp    open  http    Apache httpd 2.4.41 (Ubuntu)"""

        result = self.tool.invoke({"text": nmap_output})

        service = result["hosts"][0]["services"][0]
        assert "Apache httpd 2.4.41 (Ubuntu)" in service["version"]
