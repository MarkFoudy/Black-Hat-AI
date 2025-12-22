"""
Listing 4.2: Imports and Configuration Constants

Defines seed subdomain prefixes and WAF/CDN signature patterns
used throughout the reconnaissance pipeline.
"""

from typing import Tuple
import os

# Seed subdomain prefixes to probe
# Empty string "" represents the apex domain (e.g., example.com)
SEEDS: Tuple[str, ...] = ("", "www", "api", "dev", "staging")

# Header fragments suggesting WAF/CDN presence
# Used for lightweight header-based heuristic detection
WAF_SIGS: Tuple[str, ...] = (
    "cf-ray",
    "cloudflare",
    "x-sucuri-id",
    "akamai-",
    "x-akamai",
    "x-waf",
    "x-cdn",
    "x-edge",
    "x-amzn",
    "aws-alb",
    "fastly",
    "x-served-by",
    "x-cache",
    "x-varnish",
    "x-azure-ref",
    "x-ms-request-id",
)

# Default network timeout in seconds
DEFAULT_TIMEOUT: int = int(os.environ.get("RECON_TIMEOUT", "4"))

# Default User-Agent string for requests
DEFAULT_USER_AGENT: str = os.environ.get("RECON_USER_AGENT", "ReconSnap/1.0")

# Maximum bytes to read from robots.txt
MAX_ROBOTS_SIZE: int = 65536

# Sensitive headers to redact before persisting
SENSITIVE_HEADERS: Tuple[str, ...] = (
    "set-cookie",
    "authorization",
    "x-api-key",
    "x-auth-token",
    "cookie",
    "x-csrf-token",
)
