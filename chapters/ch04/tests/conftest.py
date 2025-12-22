"""
Shared pytest fixtures for Chapter 4 tests.
"""

import json
import os
import pytest
from typing import Dict, List
from unittest.mock import MagicMock

# Add src to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.artifacts import Artifact
from src.safety.scope import ScopeConfig, ScopeChecker


@pytest.fixture
def sample_headers() -> Dict[str, str]:
    """Sample HTTP response headers."""
    return {
        "server": "nginx/1.18.0",
        "content-type": "text/html; charset=UTF-8",
        "x-powered-by": "Express",
        "x-frame-options": "SAMEORIGIN",
    }


@pytest.fixture
def cloudflare_headers() -> Dict[str, str]:
    """Headers indicating Cloudflare WAF/CDN."""
    return {
        "server": "cloudflare",
        "cf-ray": "abc123-LAX",
        "content-type": "application/json",
    }


@pytest.fixture
def sensitive_headers() -> Dict[str, str]:
    """Headers containing sensitive data."""
    return {
        "server": "nginx",
        "set-cookie": "session=abc123; HttpOnly",
        "authorization": "Bearer secret-token",
        "x-api-key": "api-key-12345",
    }


@pytest.fixture
def temp_artifact_file(tmp_path):
    """Temporary file for artifact testing."""
    return tmp_path / "test_recon.jsonl"


@pytest.fixture
def temp_scope_file(tmp_path):
    """Temporary file for scope configuration."""
    scope_file = tmp_path / "scope.json"
    scope_data = {
        "allowed": ["example.com", "*.example.com"],
        "forbidden": ["prod.example.com"],
    }
    with open(scope_file, "w") as f:
        json.dump(scope_data, f)
    return scope_file


@pytest.fixture
def sample_artifact() -> Artifact:
    """Sample Artifact instance."""
    return Artifact(
        host="example.com",
        a=["93.184.216.34"],
        cname="example.com",
        headers={"server": "nginx"},
        waf_hint=False,
        notes=["status:200"],
    )


@pytest.fixture
def sample_scope() -> ScopeConfig:
    """Sample scope configuration."""
    return ScopeConfig(
        allowed=["example.com", "*.example.com"],
        forbidden=["prod.example.com"],
    )


@pytest.fixture
def sample_scope_checker(sample_scope) -> ScopeChecker:
    """Sample scope checker."""
    return ScopeChecker(sample_scope)


@pytest.fixture
def mock_dns_response():
    """Mocked getaddrinfo response."""
    return [
        (2, 1, 6, '', ('93.184.216.34', 80)),
        (2, 1, 6, '', ('93.184.216.34', 80)),
    ]


@pytest.fixture
def mock_ssl_socket():
    """Mocked SSL socket for TLS testing."""
    mock = MagicMock()
    mock.getpeercert.return_value = {
        "subjectAltName": [
            ("DNS", "example.com"),
            ("DNS", "www.example.com"),
        ],
        "issuer": (
            (("organizationName", "Example CA"),),
        ),
        "subject": (
            (("commonName", "example.com"),),
        ),
        "notBefore": "Jan  1 00:00:00 2025 GMT",
        "notAfter": "Jan  1 00:00:00 2026 GMT",
    }
    mock.selected_alpn_protocol.return_value = "h2"
    mock.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
    mock.version.return_value = "TLSv1.3"
    return mock


@pytest.fixture
def sample_robots_txt() -> str:
    """Sample robots.txt content."""
    return """
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-news.xml

Crawl-delay: 10
"""
