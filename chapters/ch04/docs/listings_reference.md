# Chapter 4: Listings Reference

This document maps each code listing from Chapter 4 of *Black Hat AI* to its corresponding source file in this repository.

## Listings Overview

| Listing | Title | File | Description |
|---------|-------|------|-------------|
| 4.1 | The Artifact Helper | `src/core/artifacts.py` | Artifact dataclass and JSONL I/O utilities |
| 4.2 | Imports and Configuration Constants | `src/recon/constants.py` | SEEDS, WAF_SIGS, and default values |
| 4.3 | DNS Resolution Helpers | `src/recon/dns.py` | `candidates()` and `resolve()` functions |
| 4.4 | HTTPS Probing | `src/recon/http.py` | `https_head()` function |
| 4.5 | WAF/CDN Heuristic Detection | `src/recon/waf.py` | `infer_waf()` function |
| 4.6 | TLS Certificate Inspection | `src/recon/tls.py` | `tls_peek()` function |
| 4.7 | Content Inspection | `src/recon/content.py` | `robots_and_sitemap()` function |
| 4.8 | Header Sanitization | `src/recon/sanitize.py` | `sanitize_headers()` function |
| 4.9 | Pipeline Orchestrator | `src/recon/pipeline.py` | `main()` and `ReconPipeline` class |

## Section-Based Code

| Section | Topic | File | Description |
|---------|-------|------|-------------|
| 4.2.4 | Safety Gates | `src/safety/gates.py` | Time window and approval gates |
| 4.6 | Scope Enforcement | `src/safety/scope.py` | ScopeConfig and ScopeChecker |
| 4.4 | Artifact Analysis | `scripts/analyze_results.py` | jq-equivalent analysis commands |

## Detailed Listing Breakdown

### Listing 4.1: The Artifact Helper

**File:** `src/core/artifacts.py`

```python
@dataclass
class Artifact:
    schema: str = "recon-v1"
    host: str = ""
    a: List[str] = field(default_factory=list)
    cname: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    waf_hint: Optional[bool] = None
    tls: Optional[Dict] = None
    notes: List[str] = field(default_factory=list)
    ts: str = ""
```

**Key exports:**
- `Artifact` - Dataclass for structured recon data
- `ScopeArtifact` - Dataclass for scope decisions
- `write_jsonl()` - Append artifact to JSONL file
- `read_jsonl()` - Read all artifacts from JSONL
- `iter_jsonl()` - Iterator over JSONL records

### Listing 4.2: Imports and Constants

**File:** `src/recon/constants.py`

```python
SEEDS: Tuple[str, ...] = ("", "www", "api", "dev", "staging")

WAF_SIGS: Tuple[str, ...] = (
    "cf-ray", "cloudflare", "x-sucuri-id", "akamai-", ...
)
```

**Key exports:**
- `SEEDS` - Subdomain prefixes to probe
- `WAF_SIGS` - WAF/CDN header signatures
- `DEFAULT_TIMEOUT` - Network timeout (4 seconds)
- `DEFAULT_USER_AGENT` - User-Agent string
- `SENSITIVE_HEADERS` - Headers to redact

### Listing 4.3: DNS Resolution

**File:** `src/recon/dns.py`

```python
def candidates(root: str) -> List[str]:
    return sorted({(s + "." + root).strip(".") for s in SEEDS})

def resolve(host: str) -> Tuple[List[str], Optional[str]]:
    # Returns (ip_addresses, canonical_name)
```

**Key exports:**
- `candidates()` - Generate subdomain candidates
- `resolve()` - DNS A/AAAA and CNAME lookup
- `resolve_batch()` - Resolve multiple hosts

### Listing 4.4: HTTPS Probing

**File:** `src/recon/http.py`

```python
def https_head(host: str, timeout: int = 4, ...) -> Tuple[Dict[str, str], List[str]]:
    # Returns (headers, notes)
```

**Key exports:**
- `https_head()` - Send HTTPS HEAD request
- `http_head()` - Send plain HTTP HEAD request

### Listing 4.5: WAF Detection

**File:** `src/recon/waf.py`

```python
def infer_waf(headers: Dict[str, str]) -> bool:
    # Returns True if WAF/CDN signatures detected
```

**Key exports:**
- `infer_waf()` - Boolean WAF detection
- `detect_waf_signatures()` - List matched signatures
- `classify_waf()` - Identify WAF provider

### Listing 4.6: TLS Inspection

**File:** `src/recon/tls.py`

```python
def tls_peek(host: str, timeout: int = 4) -> Dict:
    # Returns {"alpn": [...], "san": [...]}
```

**Key exports:**
- `tls_peek()` - Extract ALPN and SAN
- `get_certificate_details()` - Full cert info
- `extract_sans()` - Just the SAN list
- `discover_related_hosts()` - Find hosts from SANs

### Listing 4.7: Content Inspection

**File:** `src/recon/content.py`

```python
def robots_and_sitemap(host: str, ...) -> List[str]:
    # Returns notes like ["robots:yes", "sitemap:..."]
```

**Key exports:**
- `robots_and_sitemap()` - Check robots.txt presence
- `parse_robots_txt()` - Parse robots.txt content
- `fetch_robots_txt()` - Retrieve raw content

### Listing 4.8: Header Sanitization

**File:** `src/recon/sanitize.py`

```python
def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    # Returns headers with sensitive values redacted
```

**Key exports:**
- `sanitize_headers()` - Redact sensitive headers
- `extract_safe_headers()` - Keep only safe headers
- `get_fingerprint_headers()` - Extract tech stack headers

### Listing 4.9: Pipeline Orchestrator

**File:** `src/recon/pipeline.py`

```python
class ReconPipeline:
    def run(self, root_domain: str) -> PipelineResult:
        # Execute full pipeline

    def run_single_host(self, host: str) -> Artifact:
        # Process one host
```

**Key exports:**
- `PipelineConfig` - Configuration dataclass
- `PipelineResult` - Result dataclass
- `ReconPipeline` - Main pipeline class
- `run_pipeline()` - Convenience function
- `main()` - CLI entrypoint

## Additional Files

### Scope Enforcement (Section 4.6)

**File:** `src/safety/scope.py`

```python
class ScopeChecker:
    def is_allowed(self, host: str) -> Tuple[bool, str]:
        # Returns (allowed, reason)
```

### Safety Gates (Section 4.2.4)

**File:** `src/safety/gates.py`

```python
def time_window_gate(start_hour: int, end_hour: int) -> Tuple[bool, str]:
    # Returns (allowed, reason)

def approval_gate(action: str, target: str, ...) -> bool:
    # Returns True if approved
```

### Analysis Helpers (Section 4.4)

**File:** `scripts/analyze_results.py`

Provides CLI commands equivalent to the jq examples in the book:

| Book Command | Script Command |
|--------------|----------------|
| `grep "status:200" recon.jsonl \| jq -r '.host'` | `python scripts/analyze_results.py status-ok` |
| `jq -r 'select(.waf_hint==true) \| .host'` | `python scripts/analyze_results.py waf-detected` |
| `jq -r '.headers \| keys[]' \| sort \| uniq` | `python scripts/analyze_results.py headers` |

## Exercises

### Exercise 4.1

Run the pipeline with different flags and compare output:

```bash
python scripts/run_recon.py example.com
python scripts/run_recon.py example.com --tls
python scripts/run_recon.py example.com --content
```

### Exercise 4.2

Use the cluster-by-ip command to find hosts sharing IPs:

```bash
python scripts/analyze_results.py cluster-by-ip
```

## Tests

Each listing has corresponding tests:

| Listing | Test File |
|---------|-----------|
| 4.1 | `tests/test_core/test_artifacts.py` |
| 4.2 | `tests/test_recon/test_constants.py` |
| 4.3 | `tests/test_recon/test_dns.py` |
| 4.5 | `tests/test_recon/test_waf.py` |
| 4.8 | `tests/test_recon/test_sanitize.py` |
| §4.6 | `tests/test_safety/test_scope.py` |
| §4.2.4 | `tests/test_safety/test_gates.py` |
