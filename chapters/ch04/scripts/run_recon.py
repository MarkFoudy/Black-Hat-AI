#!/usr/bin/env python3
"""
Main CLI entrypoint for the passive reconnaissance pipeline.

Usage:
    python scripts/run_recon.py example.com
    python scripts/run_recon.py example.com --tls --content
    python scripts/run_recon.py example.com --scope data/scope.json
    python scripts/run_recon.py example.com --output runs/my_scan.jsonl
    python scripts/run_recon.py example.com --dry-run

This script wraps the ReconPipeline class with additional features:
- Scope enforcement via --scope flag
- Time window gating via --time-gate flag
- Environment variable configuration via .env file
"""

import argparse
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.artifacts import DEFAULT_OUT
from src.recon.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from src.recon.pipeline import PipelineConfig, ReconPipeline
from src.safety.scope import load_scope_safe, ScopeChecker
from src.safety.gates import time_window_gate


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Passive reconnaissance pipeline with safety gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic scan:
    python scripts/run_recon.py example.com

  Full scan with TLS and content:
    python scripts/run_recon.py example.com --tls --content

  Scoped scan:
    python scripts/run_recon.py example.com --scope data/scope.json

  Dry run (show what would be scanned):
    python scripts/run_recon.py example.com --dry-run
        """,
    )

    parser.add_argument(
        "root",
        help="Root domain to scan (e.g., example.com)",
    )
    parser.add_argument(
        "--tls",
        action="store_true",
        help="Include TLS ALPN/SAN inspection",
    )
    parser.add_argument(
        "--content",
        action="store_true",
        help="Fetch /robots.txt and extract sitemap hints",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Network timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"User-Agent string for requests (default: {DEFAULT_USER_AGENT})",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUT,
        help=f"Output file path (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--scope",
        "-s",
        help="Path to scope.json file for scope enforcement",
    )
    parser.add_argument(
        "--time-gate",
        action="store_true",
        help="Enable time window gate (default: 9:00-17:00 UTC)",
    )
    parser.add_argument(
        "--time-start",
        type=int,
        default=9,
        help="Start hour for time gate (default: 9)",
    )
    parser.add_argument(
        "--time-end",
        type=int,
        default=17,
        help="End hour for time gate (default: 17)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress messages",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scanned without executing",
    )

    args = parser.parse_args()

    # Check time gate if enabled
    if args.time_gate:
        allowed, reason = time_window_gate(args.time_start, args.time_end)
        if not allowed:
            print(f"[GATE] Time window check failed: {reason}")
            return 1
        if args.verbose:
            print(f"[GATE] Time window check passed: {reason}")

    # Load scope configuration if provided
    scope_checker = None
    if args.scope:
        scope_config = load_scope_safe(args.scope)
        if scope_config is None:
            print(f"[ERROR] Could not load scope file: {args.scope}")
            return 1
        scope_checker = ScopeChecker(scope_config)
        if args.verbose:
            print(f"[SCOPE] Loaded scope from {args.scope}")
            print(f"        Allowed: {scope_config.allowed}")
            print(f"        Forbidden: {scope_config.forbidden}")

    # Build pipeline configuration
    config = PipelineConfig(
        timeout=args.timeout,
        user_agent=args.user_agent,
        include_tls=args.tls,
        include_content=args.content,
        output_path=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose or args.dry_run,
    )

    # Create scope check function if configured
    scope_check_fn = None
    if scope_checker:
        def scope_check_fn(host: str) -> bool:
            allowed, _ = scope_checker.is_allowed(host)
            return allowed

    # Run pipeline
    pipeline = ReconPipeline(config, scope_checker=scope_check_fn)

    print(f"\n{'=' * 60}")
    print(f"Passive Reconnaissance Pipeline")
    print(f"Target: {args.root}")
    print(f"Output: {args.output}")
    print(f"Options: TLS={args.tls}, Content={args.content}")
    print(f"{'=' * 60}\n")

    result = pipeline.run(args.root)

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"Hosts scanned:    {result.hosts_scanned}")
    print(f"Hosts resolved:   {result.hosts_resolved}")
    print(f"WAF detected:     {result.hosts_with_waf}")
    if result.errors:
        print(f"Errors:           {len(result.errors)}")

    if args.dry_run:
        print(f"\n[DRY RUN] No artifacts written")
    else:
        print(f"\n[OK] Artifacts written to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
