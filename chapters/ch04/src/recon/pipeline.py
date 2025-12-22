"""
Listing 4.9: Pipeline Orchestrator

The main reconnaissance pipeline that ties all stages together:
Plan -> Act -> Observe -> Record

This module provides both a class-based interface for programmatic use
and a functional interface for simple execution.
"""

import argparse
import os
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from src.core.artifacts import Artifact, write_jsonl, DEFAULT_OUT
from src.recon.constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from src.recon.dns import candidates, resolve
from src.recon.http import https_head
from src.recon.waf import infer_waf
from src.recon.tls import tls_peek
from src.recon.content import robots_and_sitemap
from src.recon.sanitize import sanitize_headers


@dataclass
class PipelineConfig:
    """Configuration for the reconnaissance pipeline."""

    timeout: int = DEFAULT_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT
    include_tls: bool = False
    include_content: bool = False
    output_path: str = DEFAULT_OUT
    dry_run: bool = False
    verbose: bool = False


@dataclass
class PipelineResult:
    """Result of a pipeline run."""

    artifacts: List[Artifact] = field(default_factory=list)
    hosts_scanned: int = 0
    hosts_resolved: int = 0
    hosts_with_waf: int = 0
    errors: List[str] = field(default_factory=list)


class ReconPipeline:
    """
    Passive reconnaissance pipeline.

    Orchestrates the full recon flow:
    1. Plan: Generate candidate subdomains
    2. Act: Resolve DNS, probe HTTPS
    3. Observe: Extract headers, TLS info, content hints
    4. Record: Write artifacts to JSONL

    Example:
        >>> config = PipelineConfig(include_tls=True)
        >>> pipeline = ReconPipeline(config)
        >>> result = pipeline.run("example.com")
        >>> print(f"Scanned {result.hosts_scanned} hosts")
    """

    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        scope_checker: Optional[Callable[[str], bool]] = None,
    ):
        """
        Initialize the pipeline.

        Args:
            config: Pipeline configuration
            scope_checker: Optional callable that returns True if host is in scope
        """
        self.config = config or PipelineConfig()
        self.scope_checker = scope_checker

    def run(self, root_domain: str) -> PipelineResult:
        """
        Execute the full reconnaissance pipeline.

        Args:
            root_domain: Root domain to scan (e.g., "example.com")

        Returns:
            PipelineResult with all artifacts and statistics
        """
        result = PipelineResult()

        # Stage 1: Plan - Generate candidate subdomains
        hosts = [root_domain] + candidates(root_domain)

        if self.config.verbose:
            print(f"[PLAN] Generated {len(hosts)} candidate hosts")

        # Stage 2-4: Act/Observe/Record per host
        for host in hosts:
            # Check scope if configured
            if self.scope_checker and not self.scope_checker(host):
                if self.config.verbose:
                    print(f"[SKIP] {host} - out of scope")
                continue

            artifact = self.run_single_host(host)
            result.artifacts.append(artifact)
            result.hosts_scanned += 1

            if artifact.a:
                result.hosts_resolved += 1
            if artifact.waf_hint:
                result.hosts_with_waf += 1

            # Record to JSONL unless dry run
            if not self.config.dry_run:
                write_jsonl(artifact, self.config.output_path)

            if self.config.verbose:
                status = next((n for n in artifact.notes if n.startswith("status:")), "no-response")
                print(f"[SCAN] {host} - {status}")

        if self.config.verbose:
            print(f"[DONE] Scanned {result.hosts_scanned} hosts, {result.hosts_resolved} resolved")

        return result

    def run_single_host(self, host: str) -> Artifact:
        """
        Process a single host through all pipeline stages.

        Args:
            host: Hostname to scan

        Returns:
            Artifact with all gathered intelligence
        """
        # Act: DNS resolution
        ips, cname = resolve(host)

        # Act: HTTPS probe
        raw_headers, notes = https_head(
            host,
            timeout=self.config.timeout,
            user_agent=self.config.user_agent,
        )

        # Observe: Sanitize headers
        safe_headers = sanitize_headers(raw_headers)

        # Observe: WAF detection
        hint = infer_waf(safe_headers) if safe_headers else None

        # Observe: TLS inspection (optional)
        tls = None
        if self.config.include_tls:
            tls = tls_peek(host, timeout=self.config.timeout)

        # Observe: Content discovery (optional)
        if self.config.include_content:
            content_notes = robots_and_sitemap(
                host,
                timeout=self.config.timeout,
                user_agent=self.config.user_agent,
            )
            notes.extend(content_notes)

        # Record: Create artifact
        return Artifact(
            host=host,
            a=ips,
            cname=cname,
            headers=safe_headers,
            waf_hint=hint,
            tls=tls,
            notes=notes,
        )


def run_pipeline(
    root_domain: str,
    include_tls: bool = False,
    include_content: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    output_path: str = DEFAULT_OUT,
    verbose: bool = False,
) -> PipelineResult:
    """
    Convenience function to run the pipeline with common options.

    Args:
        root_domain: Root domain to scan
        include_tls: Include TLS/certificate inspection
        include_content: Include robots.txt/sitemap discovery
        timeout: Network timeout in seconds
        user_agent: User-Agent string for requests
        output_path: Path for JSONL output
        verbose: Print progress messages

    Returns:
        PipelineResult with artifacts and statistics
    """
    config = PipelineConfig(
        timeout=timeout,
        user_agent=user_agent,
        include_tls=include_tls,
        include_content=include_content,
        output_path=output_path,
        verbose=verbose,
    )
    pipeline = ReconPipeline(config)
    return pipeline.run(root_domain)


def main() -> None:
    """CLI entrypoint for the reconnaissance pipeline."""
    parser = argparse.ArgumentParser(
        description="Passive recon pipeline (single-file, append-only artifacts)"
    )
    parser.add_argument("root", help="Root domain, e.g., example.com")
    parser.add_argument(
        "--tls",
        action="store_true",
        help="Include TLS ALPN/SAN peek",
    )
    parser.add_argument(
        "--content",
        action="store_true",
        help="Fetch /robots.txt to note sitemap hints",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Network timeout seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"User-Agent for requests (default: {DEFAULT_USER_AGENT})",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUT,
        help=f"Output file path (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scanned without writing artifacts",
    )

    args = parser.parse_args()

    config = PipelineConfig(
        timeout=args.timeout,
        user_agent=args.user_agent,
        include_tls=args.tls,
        include_content=args.content,
        output_path=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose or args.dry_run,
    )

    pipeline = ReconPipeline(config)
    result = pipeline.run(args.root)

    if args.dry_run:
        print(f"\n[DRY RUN] Would scan {result.hosts_scanned} hosts")
    else:
        print(f"[OK] Recon pipeline complete — wrote {args.output}")


if __name__ == "__main__":
    main()
