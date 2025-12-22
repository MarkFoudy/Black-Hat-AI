"""
Listing 4.5: WAF/CDN Heuristic Detection

Provides lightweight header-based heuristics to detect the possible
presence of Web Application Firewalls or Content Delivery Networks.

Note: This is a hint-based detection, not definitive fingerprinting.
Full WAF profiling is covered in Chapter 5.
"""

from typing import Dict, List, Optional, Tuple

from src.recon.constants import WAF_SIGS


def infer_waf(headers: Dict[str, str]) -> bool:
    """
    Lightweight header heuristic for possible WAF/CDN presence.

    Scans response headers for telltale signatures of common
    WAFs and CDNs. Checks both header names and values.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        True if WAF/CDN signatures detected, False otherwise

    Note:
        This function errs on the side of false positives.
        It's better to flag something for closer inspection
        than to miss protection entirely.

    Example:
        >>> headers = {"server": "cloudflare", "cf-ray": "abc123"}
        >>> infer_waf(headers)
        True
    """
    # Normalize all keys and values to lowercase for comparison
    low = {
        k.lower(): (v.lower() if isinstance(v, str) else "")
        for k, v in headers.items()
    }

    for k, v in low.items():
        for sig in WAF_SIGS:
            if sig in k or sig in v:
                return True

    return False


def detect_waf_signatures(headers: Dict[str, str]) -> List[str]:
    """
    Identify which specific WAF/CDN signatures were detected.

    More detailed version of infer_waf that returns the actual
    signatures found rather than just a boolean.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        List of signature strings that were matched

    Example:
        >>> headers = {"cf-ray": "abc123", "server": "cloudflare"}
        >>> detect_waf_signatures(headers)
        ['cf-ray', 'cloudflare']
    """
    detected = []
    low = {
        k.lower(): (v.lower() if isinstance(v, str) else "")
        for k, v in headers.items()
    }

    for k, v in low.items():
        for sig in WAF_SIGS:
            if sig in k or sig in v:
                if sig not in detected:
                    detected.append(sig)

    return detected


def classify_waf(headers: Dict[str, str]) -> Tuple[Optional[str], List[str]]:
    """
    Attempt to classify the WAF/CDN provider based on headers.

    Maps detected signatures to known providers.

    Args:
        headers: Dictionary of HTTP response headers

    Returns:
        Tuple of (provider_name, matched_signatures)
        - provider_name: Best guess at the provider, or None
        - matched_signatures: List of signatures that matched

    Example:
        >>> headers = {"cf-ray": "abc123", "server": "cloudflare"}
        >>> provider, sigs = classify_waf(headers)
        >>> print(provider)
        'cloudflare'
    """
    signatures = detect_waf_signatures(headers)

    if not signatures:
        return None, []

    # Map signatures to providers
    provider_map = {
        "cloudflare": ["cf-ray", "cloudflare"],
        "akamai": ["akamai-", "x-akamai"],
        "aws": ["x-amzn", "aws-alb"],
        "fastly": ["fastly", "x-served-by"],
        "varnish": ["x-varnish"],
        "azure": ["x-azure-ref", "x-ms-request-id"],
        "sucuri": ["x-sucuri-id"],
        "generic_waf": ["x-waf"],
        "generic_cdn": ["x-cdn", "x-edge", "x-cache"],
    }

    for provider, provider_sigs in provider_map.items():
        for sig in signatures:
            if sig in provider_sigs:
                return provider, signatures

    return "unknown", signatures
