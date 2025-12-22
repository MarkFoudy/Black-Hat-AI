"""
Listing 4.8: Header Sanitization

Provides functions to sanitize HTTP headers before persisting them,
removing sensitive values like cookies and authentication tokens.
"""

from typing import Dict

from src.recon.constants import SENSITIVE_HEADERS


def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Remove obviously sensitive header values before persisting.

    Preserves header names for fingerprinting purposes but replaces
    sensitive values with "[redacted]" to prevent credential leakage
    in artifact logs.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        Dictionary with sensitive values redacted

    Example:
        >>> headers = {"server": "nginx", "set-cookie": "session=abc123"}
        >>> safe = sanitize_headers(headers)
        >>> print(safe)
        {'server': 'nginx', 'set-cookie': '[redacted]'}
    """
    redacted = {}

    for k, v in headers.items():
        lk = k.lower()

        # Check if header name starts with or matches sensitive patterns
        is_sensitive = False
        for sensitive in SENSITIVE_HEADERS:
            if lk.startswith(sensitive) or lk == sensitive:
                is_sensitive = True
                break

        if is_sensitive:
            redacted[k] = "[redacted]"
        else:
            redacted[k] = v

    return redacted


def extract_safe_headers(
    headers: Dict[str, str],
    include_keys: list | None = None,
) -> Dict[str, str]:
    """
    Extract only specific safe headers for analysis.

    Useful when you want to keep only relevant headers
    for fingerprinting or analysis.

    Args:
        headers: Dictionary of HTTP response headers
        include_keys: List of header keys to include (lowercase)
                     If None, uses a default safe list

    Returns:
        Dictionary with only the specified headers
    """
    if include_keys is None:
        include_keys = [
            "server",
            "x-powered-by",
            "content-type",
            "x-frame-options",
            "x-xss-protection",
            "x-content-type-options",
            "strict-transport-security",
            "content-security-policy",
            "x-aspnet-version",
            "x-aspnetmvc-version",
        ]

    result = {}
    for k, v in headers.items():
        if k.lower() in include_keys:
            result[k] = v

    return result


def mask_ip_in_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Mask IP addresses found in header values.

    Useful for privacy-sensitive logging where IP addresses
    in headers should be obscured.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        Dictionary with IP addresses masked
    """
    import re

    # Simple IPv4 pattern
    ip_pattern = re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")

    masked = {}
    for k, v in headers.items():
        if isinstance(v, str):
            masked[k] = ip_pattern.sub(r"\1.\2.xxx.xxx", v)
        else:
            masked[k] = v

    return masked


def get_fingerprint_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Extract headers commonly used for server fingerprinting.

    Returns only headers that reveal technology stack information.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        Dictionary with fingerprint-relevant headers only
    """
    fingerprint_keys = [
        "server",
        "x-powered-by",
        "x-aspnet-version",
        "x-aspnetmvc-version",
        "x-generator",
        "x-drupal-cache",
        "x-varnish",
        "x-magento-",
        "x-shopify-",
        "x-wordpress-",
    ]

    result = {}
    for k, v in headers.items():
        lk = k.lower()
        for fp_key in fingerprint_keys:
            if lk == fp_key or lk.startswith(fp_key):
                result[k] = v
                break

    return result
