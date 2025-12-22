#!/usr/bin/env python3
"""
Artifact Analysis Tool (Section 4.4)

Query, filter, and analyze reconnaissance artifacts from JSONL files.
Provides Python equivalents of the jq commands from the book.

Usage:
    python scripts/analyze_results.py status-ok
    python scripts/analyze_results.py waf-detected
    python scripts/analyze_results.py headers
    python scripts/analyze_results.py cluster-by-ip
    python scripts/analyze_results.py timeline
    python scripts/analyze_results.py summary
    python scripts/analyze_results.py export-csv -o results.csv
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from typing import Any, Dict, Iterator, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.artifacts import iter_jsonl, DEFAULT_OUT


def cmd_status_ok(args: argparse.Namespace) -> None:
    """Show all hosts that returned 200 OK."""
    # Equivalent to: grep "status:200" recon.jsonl | jq -r '.host'
    for record in iter_jsonl(args.input):
        notes = record.get("notes", [])
        if any("status:200" in note for note in notes):
            print(record.get("host", ""))


def cmd_waf_detected(args: argparse.Namespace) -> None:
    """Find hosts with WAF/CDN detected."""
    # Equivalent to: jq -r 'select(.waf_hint==true) | .host' recon.jsonl
    for record in iter_jsonl(args.input):
        if record.get("waf_hint") is True:
            print(record.get("host", ""))


def cmd_headers(args: argparse.Namespace) -> None:
    """Extract unique header keys across all artifacts."""
    # Equivalent to: jq -r '.headers | keys[]' recon.jsonl | sort | uniq
    header_keys = set()
    for record in iter_jsonl(args.input):
        headers = record.get("headers", {})
        header_keys.update(headers.keys())

    for key in sorted(header_keys):
        print(key)


def cmd_cluster_by_ip(args: argparse.Namespace) -> None:
    """Group hosts by IP address (Exercise 4.2)."""
    ip_to_hosts: Dict[str, List[str]] = defaultdict(list)

    for record in iter_jsonl(args.input):
        host = record.get("host", "")
        ips = record.get("a", [])
        for ip in ips:
            ip_to_hosts[ip].append(host)

    # Print clusters with more than one host
    print("IP Address -> Hosts")
    print("-" * 60)
    for ip, hosts in sorted(ip_to_hosts.items()):
        if len(hosts) > 1 or args.all:
            print(f"{ip}")
            for host in sorted(hosts):
                print(f"  - {host}")
            print()


def cmd_timeline(args: argparse.Namespace) -> None:
    """Show artifacts in chronological order."""
    records = list(iter_jsonl(args.input))
    # Sort by timestamp
    records.sort(key=lambda r: r.get("ts", ""))

    for record in records:
        ts = record.get("ts", "")
        host = record.get("host", "")
        notes = record.get("notes", [])
        status = next((n for n in notes if n.startswith("status:")), "no-response")
        waf = "WAF" if record.get("waf_hint") else ""
        print(f"{ts}  {host:<40} {status:<12} {waf}")


def cmd_summary(args: argparse.Namespace) -> None:
    """Show summary statistics for the artifact file."""
    records = list(iter_jsonl(args.input))

    if not records:
        print("No artifacts found.")
        return

    # Calculate statistics
    total = len(records)
    resolved = sum(1 for r in records if r.get("a"))
    waf_detected = sum(1 for r in records if r.get("waf_hint"))
    with_tls = sum(1 for r in records if r.get("tls"))

    # Count status codes
    status_counts: Dict[str, int] = defaultdict(int)
    for record in records:
        for note in record.get("notes", []):
            if note.startswith("status:"):
                status_counts[note] += 1
            elif note.startswith("error:"):
                status_counts["errors"] += 1

    # Get unique IPs
    all_ips = set()
    for record in records:
        all_ips.update(record.get("a", []))

    print("=" * 60)
    print("Reconnaissance Summary")
    print("=" * 60)
    print(f"Total hosts scanned:     {total}")
    print(f"Hosts resolved:          {resolved}")
    print(f"Unique IP addresses:     {len(all_ips)}")
    print(f"WAF/CDN detected:        {waf_detected}")
    print(f"With TLS info:           {with_tls}")
    print()
    print("Status breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    # Time range
    timestamps = [r.get("ts", "") for r in records if r.get("ts")]
    if timestamps:
        print()
        print(f"Time range:")
        print(f"  First: {min(timestamps)}")
        print(f"  Last:  {max(timestamps)}")


def cmd_export_csv(args: argparse.Namespace) -> None:
    """Export artifacts to CSV format."""
    records = list(iter_jsonl(args.input))

    if not records:
        print("No artifacts to export.")
        return

    # Define CSV columns
    fieldnames = [
        "host",
        "ips",
        "cname",
        "status",
        "waf_hint",
        "server",
        "tls_alpn",
        "tls_san",
        "notes",
        "timestamp",
    ]

    output = args.output or "recon_export.csv"

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            # Extract status from notes
            notes = record.get("notes", [])
            status = next((n for n in notes if n.startswith("status:")), "")

            # Extract server header
            headers = record.get("headers", {})
            server = headers.get("server", "")

            # Extract TLS info
            tls = record.get("tls", {}) or {}

            row = {
                "host": record.get("host", ""),
                "ips": ";".join(record.get("a", [])),
                "cname": record.get("cname", ""),
                "status": status,
                "waf_hint": record.get("waf_hint", ""),
                "server": server,
                "tls_alpn": ";".join(tls.get("alpn", [])),
                "tls_san": ";".join(tls.get("san", [])),
                "notes": ";".join(notes),
                "timestamp": record.get("ts", ""),
            }
            writer.writerow(row)

    print(f"Exported {len(records)} records to {output}")


def cmd_hosts(args: argparse.Namespace) -> None:
    """List all scanned hosts."""
    for record in iter_jsonl(args.input):
        print(record.get("host", ""))


def cmd_errors(args: argparse.Namespace) -> None:
    """Show hosts with errors."""
    for record in iter_jsonl(args.input):
        notes = record.get("notes", [])
        errors = [n for n in notes if n.startswith("error:")]
        if errors:
            host = record.get("host", "")
            print(f"{host}: {', '.join(errors)}")


def cmd_json(args: argparse.Namespace) -> None:
    """Pretty-print artifacts as JSON."""
    for record in iter_jsonl(args.input):
        print(json.dumps(record, indent=2))


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Analyze reconnaissance artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        default=DEFAULT_OUT,
        help=f"Input JSONL file (default: {DEFAULT_OUT})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Analysis command")

    # status-ok
    sub = subparsers.add_parser("status-ok", help="Show hosts that returned 200 OK")
    sub.set_defaults(func=cmd_status_ok)

    # waf-detected
    sub = subparsers.add_parser("waf-detected", help="Show hosts with WAF/CDN detected")
    sub.set_defaults(func=cmd_waf_detected)

    # headers
    sub = subparsers.add_parser("headers", help="Extract unique header keys")
    sub.set_defaults(func=cmd_headers)

    # cluster-by-ip
    sub = subparsers.add_parser("cluster-by-ip", help="Group hosts by IP address")
    sub.add_argument("--all", action="store_true", help="Show all clusters, not just multi-host")
    sub.set_defaults(func=cmd_cluster_by_ip)

    # timeline
    sub = subparsers.add_parser("timeline", help="Show chronological timeline")
    sub.set_defaults(func=cmd_timeline)

    # summary
    sub = subparsers.add_parser("summary", help="Show summary statistics")
    sub.set_defaults(func=cmd_summary)

    # export-csv
    sub = subparsers.add_parser("export-csv", help="Export to CSV format")
    sub.add_argument("--output", "-o", help="Output CSV file")
    sub.set_defaults(func=cmd_export_csv)

    # hosts
    sub = subparsers.add_parser("hosts", help="List all scanned hosts")
    sub.set_defaults(func=cmd_hosts)

    # errors
    sub = subparsers.add_parser("errors", help="Show hosts with errors")
    sub.set_defaults(func=cmd_errors)

    # json
    sub = subparsers.add_parser("json", help="Pretty-print as JSON")
    sub.set_defaults(func=cmd_json)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1

    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
