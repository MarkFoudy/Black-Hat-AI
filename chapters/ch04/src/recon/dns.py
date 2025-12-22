"""
Listing 4.3: DNS Resolution Helpers

Provides functions for generating candidate subdomains and
performing DNS resolution to retrieve IP addresses.
"""

import socket
from typing import List, Optional, Tuple

from src.recon.constants import SEEDS


def candidates(root: str) -> List[str]:
    """
    Generate candidate subdomains from seed prefixes.

    Combines each seed prefix with the root domain to create
    a list of potential subdomains to probe.

    Args:
        root: Root domain (e.g., "example.com")

    Returns:
        Sorted list of candidate hostnames
        e.g., ["api.example.com", "dev.example.com", "example.com", ...]

    Example:
        >>> candidates("example.com")
        ['api.example.com', 'dev.example.com', 'example.com', 'staging.example.com', 'www.example.com']
    """
    # Use set comprehension to automatically deduplicate
    # Empty seed produces just the root domain
    return sorted({(s + "." + root).strip(".") for s in SEEDS})


def resolve(host: str) -> Tuple[List[str], Optional[str]]:
    """
    Perform best-effort A/AAAA resolution and primary name lookup.

    Uses socket.getaddrinfo() for IP resolution and
    socket.gethostbyname_ex() for canonical name lookup.

    Args:
        host: Hostname to resolve

    Returns:
        Tuple of (ip_addresses, canonical_name)
        - ip_addresses: Sorted list of IPv4/IPv6 addresses
        - canonical_name: Primary/canonical name if available, else None

    Note:
        Both calls are wrapped in try/except because failed lookups
        are expected for non-existent subdomains.

    Example:
        >>> ips, cname = resolve("www.example.com")
        >>> print(ips)
        ['93.184.216.34']
    """
    # Resolve A/AAAA records
    try:
        infos = socket.getaddrinfo(host, 80, proto=socket.IPPROTO_TCP)
        ips = sorted({ai[4][0] for ai in infos})
    except (socket.gaierror, socket.herror, OSError):
        ips = []

    # Get canonical name (best-effort)
    try:
        primary, _aliases, _ips = socket.gethostbyname_ex(host)
        cname = primary
    except (socket.gaierror, socket.herror, OSError):
        cname = None

    return ips, cname


def resolve_batch(hosts: List[str]) -> List[Tuple[str, List[str], Optional[str]]]:
    """
    Resolve multiple hosts and return results.

    Args:
        hosts: List of hostnames to resolve

    Returns:
        List of tuples (host, ips, cname) for each input host
    """
    results = []
    for host in hosts:
        ips, cname = resolve(host)
        results.append((host, ips, cname))
    return results
