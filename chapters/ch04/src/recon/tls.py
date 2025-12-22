"""
Listing 4.6: TLS Certificate Inspection

Provides functions to peek at TLS certificate metadata including
ALPN negotiation results and Subject Alternative Names (SANs).
"""

import socket
import ssl
from typing import Any, Dict, List, Optional

from src.recon.constants import DEFAULT_TIMEOUT


def tls_peek(host: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Peek at ALPN and SAN without fetching content.

    Performs a TLS handshake to extract:
    - ALPN result (reveals supported protocols like HTTP/2)
    - SAN list from certificate (often exposes additional hostnames)

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with:
        - alpn: List of negotiated protocols (e.g., ["h2"])
        - san: List of DNS names from Subject Alternative Name

    Example:
        >>> tls_info = tls_peek("example.com")
        >>> print(tls_info)
        {'alpn': ['h2'], 'san': ['example.com', 'www.example.com']}
    """
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert() or {}
                alpn = ssock.selected_alpn_protocol()

        # Extract DNS names from Subject Alternative Name
        sans = [v for (t, v) in cert.get("subjectAltName", []) if t == "DNS"]

        return {"alpn": [alpn] if alpn else [], "san": sans}

    except ssl.SSLError:
        return {"alpn": [], "san": [], "error": "SSLError"}
    except (ConnectionError, TimeoutError, OSError):
        return {"alpn": [], "san": []}


def get_certificate_details(host: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Get detailed TLS certificate information.

    Extended version of tls_peek that extracts more certificate
    metadata for deeper analysis.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with certificate details including:
        - alpn: Negotiated protocols
        - san: Subject Alternative Names
        - issuer: Certificate issuer
        - subject: Certificate subject
        - not_before: Validity start date
        - not_after: Validity end date
        - version: Certificate version
    """
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert() or {}
                alpn = ssock.selected_alpn_protocol()
                cipher = ssock.cipher()
                version = ssock.version()

        sans = [v for (t, v) in cert.get("subjectAltName", []) if t == "DNS"]

        # Extract issuer and subject as readable strings
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))

        return {
            "alpn": [alpn] if alpn else [],
            "san": sans,
            "issuer": issuer.get("organizationName", issuer.get("commonName", "")),
            "subject": subject.get("commonName", ""),
            "not_before": cert.get("notBefore", ""),
            "not_after": cert.get("notAfter", ""),
            "serial_number": cert.get("serialNumber", ""),
            "cipher": cipher[0] if cipher else None,
            "tls_version": version,
        }

    except ssl.SSLError as e:
        return {"error": f"SSLError: {e.reason if hasattr(e, 'reason') else str(e)}"}
    except (ConnectionError, TimeoutError, OSError) as e:
        return {"error": f"{type(e).__name__}"}


def extract_sans(host: str, timeout: int = DEFAULT_TIMEOUT) -> List[str]:
    """
    Extract just the Subject Alternative Names from a certificate.

    Convenience function for when you only need the SAN list.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds

    Returns:
        List of DNS names from the certificate's SAN extension
    """
    result = tls_peek(host, timeout)
    return result.get("san", [])


def discover_related_hosts(host: str, timeout: int = DEFAULT_TIMEOUT) -> List[str]:
    """
    Discover potentially related hosts from certificate SANs.

    SANs often reveal additional subdomains or related services
    that share the same certificate.

    Args:
        host: Target hostname
        timeout: Connection timeout in seconds

    Returns:
        List of discovered hostnames (excluding the input host)
    """
    sans = extract_sans(host, timeout)
    # Filter out the original host and wildcards
    related = [
        s for s in sans
        if s != host and not s.startswith("*.")
    ]
    return sorted(set(related))
