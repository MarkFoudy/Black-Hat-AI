"""
Recon module for Chapter 4: Passive Reconnaissance Agents.

Provides passive reconnaissance capabilities including DNS resolution,
HTTPS probing, WAF detection, TLS inspection, and content discovery.
"""

from src.recon.constants import (
    SEEDS,
    WAF_SIGS,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
    SENSITIVE_HEADERS,
)
from src.recon.dns import candidates, resolve, resolve_batch
from src.recon.http import https_head, http_head
from src.recon.waf import infer_waf, detect_waf_signatures, classify_waf
from src.recon.tls import tls_peek, get_certificate_details, extract_sans, discover_related_hosts
from src.recon.content import robots_and_sitemap, parse_robots_txt, fetch_robots_txt
from src.recon.sanitize import (
    sanitize_headers,
    extract_safe_headers,
    mask_ip_in_headers,
    get_fingerprint_headers,
)
from src.recon.pipeline import (
    PipelineConfig,
    PipelineResult,
    ReconPipeline,
    run_pipeline,
)

__all__ = [
    # Constants
    "SEEDS",
    "WAF_SIGS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_USER_AGENT",
    "SENSITIVE_HEADERS",
    # DNS
    "candidates",
    "resolve",
    "resolve_batch",
    # HTTP
    "https_head",
    "http_head",
    # WAF
    "infer_waf",
    "detect_waf_signatures",
    "classify_waf",
    # TLS
    "tls_peek",
    "get_certificate_details",
    "extract_sans",
    "discover_related_hosts",
    # Content
    "robots_and_sitemap",
    "parse_robots_txt",
    "fetch_robots_txt",
    # Sanitize
    "sanitize_headers",
    "extract_safe_headers",
    "mask_ip_in_headers",
    "get_fingerprint_headers",
    # Pipeline
    "PipelineConfig",
    "PipelineResult",
    "ReconPipeline",
    "run_pipeline",
]
