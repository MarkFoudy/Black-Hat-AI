"""
Tests for src/recon/sanitize.py (Listing 4.8)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.recon.sanitize import (
    sanitize_headers,
    extract_safe_headers,
    mask_ip_in_headers,
    get_fingerprint_headers,
)


class TestSanitizeHeaders:
    """Tests for the sanitize_headers function."""

    def test_sanitize_redacts_cookies(self, sensitive_headers):
        """Test redaction of Set-Cookie header."""
        result = sanitize_headers(sensitive_headers)
        assert result["set-cookie"] == "[redacted]"

    def test_sanitize_redacts_authorization(self, sensitive_headers):
        """Test redaction of Authorization header."""
        result = sanitize_headers(sensitive_headers)
        assert result["authorization"] == "[redacted]"

    def test_sanitize_redacts_api_key(self, sensitive_headers):
        """Test redaction of X-API-Key header."""
        result = sanitize_headers(sensitive_headers)
        assert result["x-api-key"] == "[redacted]"

    def test_sanitize_preserves_safe_headers(self, sample_headers):
        """Test that safe headers are preserved."""
        result = sanitize_headers(sample_headers)
        assert result["server"] == "nginx/1.18.0"
        assert result["content-type"] == "text/html; charset=UTF-8"

    def test_sanitize_empty_headers(self):
        """Test handling of empty headers."""
        result = sanitize_headers({})
        assert result == {}

    def test_sanitize_case_insensitive(self):
        """Test case-insensitive header matching."""
        headers = {"SET-COOKIE": "session=abc", "AUTHORIZATION": "Bearer xyz"}
        result = sanitize_headers(headers)
        assert result["SET-COOKIE"] == "[redacted]"
        assert result["AUTHORIZATION"] == "[redacted]"


class TestExtractSafeHeaders:
    """Tests for the extract_safe_headers function."""

    def test_extract_default_headers(self, sample_headers):
        """Test extraction with default include list."""
        result = extract_safe_headers(sample_headers)
        assert "server" in result
        assert "x-powered-by" in result

    def test_extract_custom_headers(self):
        """Test extraction with custom include list."""
        headers = {"server": "nginx", "custom-header": "value", "x-test": "test"}
        result = extract_safe_headers(headers, include_keys=["server", "x-test"])
        assert "server" in result
        assert "x-test" in result
        assert "custom-header" not in result

    def test_extract_empty_result(self):
        """Test extraction when no headers match."""
        headers = {"custom-only": "value"}
        result = extract_safe_headers(headers, include_keys=["server"])
        assert result == {}


class TestMaskIpInHeaders:
    """Tests for the mask_ip_in_headers function."""

    def test_mask_ip_addresses(self):
        """Test IP address masking."""
        headers = {"x-forwarded-for": "192.168.1.100"}
        result = mask_ip_in_headers(headers)
        assert "xxx" in result["x-forwarded-for"]
        assert "192.168" in result["x-forwarded-for"]

    def test_mask_multiple_ips(self):
        """Test masking multiple IP addresses."""
        headers = {"x-forwarded-for": "192.168.1.100, 10.0.0.50"}
        result = mask_ip_in_headers(headers)
        assert "192.168.xxx.xxx" in result["x-forwarded-for"]
        assert "10.0.xxx.xxx" in result["x-forwarded-for"]

    def test_mask_preserves_non_ip_values(self):
        """Test that non-IP values are preserved."""
        headers = {"server": "nginx", "x-request-id": "abc123"}
        result = mask_ip_in_headers(headers)
        assert result["server"] == "nginx"
        assert result["x-request-id"] == "abc123"


class TestGetFingerprintHeaders:
    """Tests for the get_fingerprint_headers function."""

    def test_fingerprint_extracts_server(self, sample_headers):
        """Test extraction of server header."""
        result = get_fingerprint_headers(sample_headers)
        assert "server" in result

    def test_fingerprint_extracts_x_powered_by(self, sample_headers):
        """Test extraction of X-Powered-By header."""
        result = get_fingerprint_headers(sample_headers)
        assert "x-powered-by" in result

    def test_fingerprint_ignores_irrelevant(self, sample_headers):
        """Test that irrelevant headers are ignored."""
        result = get_fingerprint_headers(sample_headers)
        assert "content-type" not in result
        assert "x-frame-options" not in result
