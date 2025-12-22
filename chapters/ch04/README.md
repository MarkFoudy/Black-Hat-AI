# Chapter 4: Passive Reconnaissance Agents

Code companion for **Chapter 4** of *Black Hat AI: Offensive Security with Large Language Models*.

## Overview

This chapter introduces building AI-driven passive reconnaissance pipelines. You'll learn:

- **Pipeline Architecture**: Why pipelines outperform one-off scripts
- **ReAct Pattern**: Plan, Act, Observe, Record workflow
- **Structured Artifacts**: JSONL-based audit trails for transparency
- **Safety Gates**: Time windows, scope enforcement, and approval checks
- **Modular Design**: Composable reconnaissance stages

## Quick Start

### 1. Install Dependencies

```bash
# Core functionality requires NO external dependencies (stdlib only)
# Just run directly:
python scripts/run_recon.py example.com

# Optional: Install enhanced CLI and development tools
pip install -e .[all]
```

### 2. Run Your First Scan

```bash
# Basic passive recon
python scripts/run_recon.py example.com

# With TLS inspection and content discovery
python scripts/run_recon.py example.com --tls --content

# Dry run to see what would be scanned
python scripts/run_recon.py example.com --dry-run --verbose
```

### 3. Analyze Results

```bash
# View summary statistics
python scripts/analyze_results.py summary

# Find hosts with WAF detected
python scripts/analyze_results.py waf-detected

# Export to CSV
python scripts/analyze_results.py export-csv -o results.csv
```

## Project Structure

```
ch04/
├── src/                        # Core library code
│   ├── core/                   # Foundational abstractions
│   │   └── artifacts.py        # Artifact dataclass + JSONL I/O
│   ├── recon/                  # Reconnaissance modules
│   │   ├── constants.py        # SEEDS, WAF_SIGS, defaults
│   │   ├── dns.py              # DNS resolution
│   │   ├── http.py             # HTTPS probing
│   │   ├── waf.py              # WAF/CDN detection
│   │   ├── tls.py              # TLS certificate inspection
│   │   ├── content.py          # robots.txt parsing
│   │   ├── sanitize.py         # Header sanitization
│   │   └── pipeline.py         # Pipeline orchestrator
│   └── safety/                 # Safety mechanisms
│       ├── scope.py            # Scope enforcement
│       └── gates.py            # Safety gates
├── scripts/                    # Runnable examples
│   ├── run_recon.py            # Main CLI entrypoint
│   ├── analyze_results.py      # Artifact analysis tool
│   └── example_with_scope.py   # Scope enforcement demo
├── data/                       # Sample data
│   ├── scope.json              # Example scope configuration
│   └── sample_recon.jsonl      # Example output artifacts
├── tests/                      # Unit tests
├── docs/                       # Additional documentation
├── logs/                       # Runtime logs
└── runs/                       # Artifact outputs
```

## Finding Code Listings

Every source file corresponds to listings from the book.

| Listing | Description | File Location |
|---------|-------------|---------------|
| 4.1 | Artifact helper | `src/core/artifacts.py` |
| 4.2 | Imports and constants | `src/recon/constants.py` |
| 4.3 | DNS resolution helpers | `src/recon/dns.py` |
| 4.4 | HTTPS probing | `src/recon/http.py` |
| 4.5 | WAF/CDN heuristic | `src/recon/waf.py` |
| 4.6 | TLS certificate inspection | `src/recon/tls.py` |
| 4.7 | Content inspection | `src/recon/content.py` |
| 4.8 | Header sanitization | `src/recon/sanitize.py` |
| 4.9 | Pipeline orchestrator | `src/recon/pipeline.py` |
| §4.6 | Scope enforcement | `src/safety/scope.py` |
| §4.2.4 | Safety gates | `src/safety/gates.py` |

See [`docs/listings_reference.md`](docs/listings_reference.md) for detailed mapping.

## Running Examples

### Basic Reconnaissance

```bash
# Scan a domain
python scripts/run_recon.py example.com

# With all options
python scripts/run_recon.py example.com --tls --content --verbose
```

### Scoped Reconnaissance

```bash
# Use scope file to limit targets
python scripts/run_recon.py example.com --scope data/scope.json

# Run scope examples
python scripts/example_with_scope.py
```

### Analyzing Results

```bash
# Summary statistics
python scripts/analyze_results.py summary

# Find hosts returning 200 OK
python scripts/analyze_results.py status-ok

# Find WAF-protected hosts
python scripts/analyze_results.py waf-detected

# Group hosts by IP (cluster analysis)
python scripts/analyze_results.py cluster-by-ip

# View timeline
python scripts/analyze_results.py timeline

# Export to CSV
python scripts/analyze_results.py export-csv -o results.csv
```

## Using the Library

### Basic Pipeline Usage

```python
from src.recon.pipeline import ReconPipeline, PipelineConfig

config = PipelineConfig(
    include_tls=True,
    include_content=True,
    verbose=True,
)

pipeline = ReconPipeline(config)
result = pipeline.run("example.com")

print(f"Scanned {result.hosts_scanned} hosts")
print(f"WAF detected on {result.hosts_with_waf} hosts")
```

### With Scope Enforcement

```python
from src.recon.pipeline import ReconPipeline, PipelineConfig
from src.safety.scope import load_scope, ScopeChecker

# Load scope configuration
scope_config = load_scope("data/scope.json")
checker = ScopeChecker(scope_config)

# Create scope check function
def scope_check(host: str) -> bool:
    allowed, _ = checker.is_allowed(host)
    return allowed

# Run pipeline with scope
config = PipelineConfig(include_tls=True)
pipeline = ReconPipeline(config, scope_checker=scope_check)
result = pipeline.run("example.com")
```

### Reading Artifacts

```python
from src.core.artifacts import read_artifacts, iter_jsonl

# Read as Artifact objects
artifacts = read_artifacts("runs/recon.jsonl")
for art in artifacts:
    print(f"{art.host}: {art.notes}")

# Iterate over raw records
for record in iter_jsonl("runs/recon.jsonl"):
    if record.get("waf_hint"):
        print(f"WAF detected: {record['host']}")
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_recon/test_waf.py -v
```

### Code Formatting

```bash
# Format code
black src/ scripts/ tests/

# Lint
ruff check src/ scripts/ tests/

# Type checking
mypy src/
```

## Key Concepts

### ReAct Pattern

The pipeline follows the ReAct (Reason + Act) pattern:

1. **Plan**: Generate candidate subdomains from seeds
2. **Act**: Resolve DNS, send HTTPS HEAD requests
3. **Observe**: Extract headers, TLS info, content hints
4. **Record**: Write structured artifacts to JSONL

### Artifact Schema

Each reconnaissance artifact contains:

```json
{
  "schema": "recon-v1",
  "host": "api.example.com",
  "a": ["93.184.216.34"],
  "cname": "api.example.com",
  "headers": {"server": "cloudflare"},
  "waf_hint": true,
  "tls": {"alpn": ["h2"], "san": ["api.example.com"]},
  "notes": ["status:200", "robots:yes"],
  "ts": "2025-10-28T14:03:11Z"
}
```

### Scope Enforcement

Scope configuration defines allowed and forbidden targets:

```json
{
  "allowed": ["example.com", "*.example.com"],
  "forbidden": ["prod.example.com", "*.gov"]
}
```

Forbidden patterns take precedence over allowed patterns.

### Safety Gates

Built-in gates ensure responsible operation:

- **Time Window Gate**: Restrict runs to approved hours
- **Scope Gate**: Enforce target boundaries
- **Approval Gate**: Require explicit confirmation
- **Rate Limit Gate**: Prevent excessive requests

## Security Considerations

This code is designed for **authorized security testing only**.

- Never run against systems you don't own or have permission to test
- Always configure scope to limit targets
- Review artifacts for sensitive data before sharing
- Use safety gates in automated pipelines
- Keep output files secure (they contain reconnaissance data)

## Troubleshooting

### No artifacts created

Ensure the `runs/` directory exists:
```bash
mkdir -p runs
```

### SSL certificate errors

Some hosts may have invalid certificates. The pipeline logs these as errors in the notes field.

### DNS resolution failures

Non-existent subdomains are expected to fail. Check the notes field for `error:` entries.

## Additional Resources

- **Book**: *Black Hat AI* by [Authors]
- **Chapter 5**: Active reconnaissance and WAF fingerprinting
- **Chapter 2**: Agent architecture foundations

## License

See the root LICENSE file.

## Contributing

This is companion code for a book. For issues or suggestions, please open an issue on the main repository.
