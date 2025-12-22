"""
Tests for src/recon/constants.py (Listing 4.2)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.recon.constants import (
    SEEDS,
    WAF_SIGS,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    SENSITIVE_HEADERS,
)


class TestConstants:
    """Tests for module constants."""

    def test_seeds_contains_common_prefixes(self):
        """Test SEEDS contains expected subdomain prefixes."""
        assert "" in SEEDS  # apex domain
        assert "www" in SEEDS
        assert "api" in SEEDS

    def test_seeds_is_tuple(self):
        """Test SEEDS is immutable tuple."""
        assert isinstance(SEEDS, tuple)

    def test_waf_sigs_contains_cloudflare(self):
        """Test WAF_SIGS contains Cloudflare signatures."""
        assert "cf-ray" in WAF_SIGS
        assert "cloudflare" in WAF_SIGS

    def test_waf_sigs_contains_akamai(self):
        """Test WAF_SIGS contains Akamai signatures."""
        assert any("akamai" in sig for sig in WAF_SIGS)

    def test_waf_sigs_is_tuple(self):
        """Test WAF_SIGS is immutable tuple."""
        assert isinstance(WAF_SIGS, tuple)

    def test_default_timeout_is_positive(self):
        """Test DEFAULT_TIMEOUT is a positive integer."""
        assert isinstance(DEFAULT_TIMEOUT, int)
        assert DEFAULT_TIMEOUT > 0

    def test_default_user_agent_not_empty(self):
        """Test DEFAULT_USER_AGENT is not empty."""
        assert isinstance(DEFAULT_USER_AGENT, str)
        assert len(DEFAULT_USER_AGENT) > 0

    def test_sensitive_headers_contains_cookie(self):
        """Test SENSITIVE_HEADERS contains cookie-related headers."""
        assert "set-cookie" in SENSITIVE_HEADERS
        assert "authorization" in SENSITIVE_HEADERS
