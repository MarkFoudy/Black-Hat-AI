"""
Tests for src/recon/waf.py (Listing 4.5)
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.recon.waf import infer_waf, detect_waf_signatures, classify_waf


class TestInferWaf:
    """Tests for the infer_waf function."""

    def test_infer_waf_detects_cloudflare(self, cloudflare_headers):
        """Test detection of Cloudflare headers."""
        assert infer_waf(cloudflare_headers) is True

    def test_infer_waf_no_waf(self, sample_headers):
        """Test no false positive on normal headers."""
        assert infer_waf(sample_headers) is False

    def test_infer_waf_empty_headers(self):
        """Test handling of empty headers."""
        assert infer_waf({}) is False

    def test_infer_waf_case_insensitive(self):
        """Test case-insensitive detection."""
        headers = {"SERVER": "CLOUDFLARE"}
        assert infer_waf(headers) is True

    def test_infer_waf_detects_in_value(self):
        """Test detection in header values."""
        headers = {"x-served-by": "cloudflare-server-123"}
        assert infer_waf(headers) is True

    def test_infer_waf_detects_akamai(self):
        """Test detection of Akamai headers."""
        headers = {"x-akamai-request-id": "abc123"}
        assert infer_waf(headers) is True

    def test_infer_waf_detects_aws(self):
        """Test detection of AWS headers."""
        headers = {"x-amzn-requestid": "abc123"}
        assert infer_waf(headers) is True


class TestDetectWafSignatures:
    """Tests for the detect_waf_signatures function."""

    def test_detect_signatures_cloudflare(self, cloudflare_headers):
        """Test extracting Cloudflare signatures."""
        sigs = detect_waf_signatures(cloudflare_headers)
        assert "cf-ray" in sigs
        assert "cloudflare" in sigs

    def test_detect_signatures_empty(self, sample_headers):
        """Test no signatures on normal headers."""
        sigs = detect_waf_signatures(sample_headers)
        assert sigs == []

    def test_detect_signatures_no_duplicates(self):
        """Test signature list has no duplicates."""
        headers = {
            "server": "cloudflare",
            "cf-ray": "abc",
            "x-cache": "cloudflare",
        }
        sigs = detect_waf_signatures(headers)
        assert len(sigs) == len(set(sigs))


class TestClassifyWaf:
    """Tests for the classify_waf function."""

    def test_classify_cloudflare(self, cloudflare_headers):
        """Test classification of Cloudflare."""
        provider, sigs = classify_waf(cloudflare_headers)
        assert provider == "cloudflare"
        assert len(sigs) > 0

    def test_classify_no_waf(self, sample_headers):
        """Test classification when no WAF present."""
        provider, sigs = classify_waf(sample_headers)
        assert provider is None
        assert sigs == []

    def test_classify_akamai(self):
        """Test classification of Akamai."""
        headers = {"x-akamai-request-id": "abc"}
        provider, _ = classify_waf(headers)
        assert provider == "akamai"

    def test_classify_aws(self):
        """Test classification of AWS."""
        headers = {"x-amzn-trace-id": "abc"}
        provider, _ = classify_waf(headers)
        assert provider == "aws"

    def test_classify_fastly(self):
        """Test classification of Fastly."""
        headers = {"fastly-restarts": "1"}
        provider, _ = classify_waf(headers)
        assert provider == "fastly"
