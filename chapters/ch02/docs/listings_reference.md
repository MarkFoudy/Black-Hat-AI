# Chapter 2: Code Listings Reference

Complete cross-reference between book listings and source code files.

## Core Abstractions

### Listing 2.1: Message & Observation Models
- **File**: `src/core/models.py`
- **Description**: Foundational data structures for agent communication
- **Classes**:
  - `Message`: Represents messages between components (user, agent, tool, system)
  - `Observation`: Captures tool execution results and metadata
- **Usage**: `from src.core.models import Message, Observation`

### Listing 2.2: Tool Base Class
- **File**: `src/core/tool.py`
- **Description**: Abstract interface that all tools must implement
- **Classes**: `Tool`
- **Key Method**: `invoke(input: Dict) -> Dict`
- **Usage**: Subclass `Tool` and implement `invoke()` method

## Minimal Agent Tools

### Listing 2.3: ExtractUrlsTool
- **File**: `src/tools/extract_urls.py`
- **Description**: Extracts URLs from text using regex
- **Classes**: `ExtractUrlsTool`
- **Usage**:
  ```python
  from src.tools.extract_urls import ExtractUrlsTool

  tool = ExtractUrlsTool()
  result = tool.invoke({"text": "Visit https://example.com"})
  print(result["urls"])  # ["https://example.com"]
  ```

### Listing 2.4: SummarizeUrlsTool
- **File**: `src/tools/summarize_urls.py`
- **Description**: Summarizes extracted URLs
- **Classes**: `SummarizeUrlsTool`
- **Usage**:
  ```python
  from src.tools.summarize_urls import SummarizeUrlsTool

  tool = SummarizeUrlsTool()
  result = tool.invoke({"urls": ["https://example.com", "https://test.com"]})
  print(result)  # {"count": 2, "summary": "Found 2 URLs."}
  ```

## Logging & Artifacts

### Listing 2.5: Artifact Logger
- **File**: `src/core/logger.py`
- **Description**: JSONL-based audit logging
- **Classes**: `ArtifactLogger`
- **Key Methods**:
  - `write(record: Dict)`: Log structured data
- **Output**: Writes to `runs/<uuid>.jsonl`
- **Usage**:
  ```python
  with ArtifactLogger() as logger:
      logger.write({"action": "scan", "target": "example.com"})
  ```

### Listing 2.9: Artifact Record Format
- **File**: `src/core/logger.py` (write method)
- **Description**: Structure of logged records
- **Example**:
  ```python
  record = {
      "run_id": run_id,
      "agent": "triage",
      "stage": "recon",
      "timestamp": timestamp,
      "input": input_data,
      "output": output_data,
      "approved_by": user_email,
      "status": "success"
  }
  logger.write(record)
  ```

## Agent Implementation

### Listing 2.6: MinimalAgent
- **File**: `src/core/agent.py`
- **Description**: Pure Python agent with explicit orchestration
- **Classes**: `MinimalAgent`
- **Key Methods**:
  - `run(text: str) -> Dict`: Execute the agent workflow
- **Features**:
  - No framework dependencies
  - No LLM calls
  - Sequential tool execution
  - Complete artifact logging
- **Usage**:
  ```python
  from src.core.agent import MinimalAgent
  from src.core.logger import ArtifactLogger
  from src.tools.extract_urls import ExtractUrlsTool
  from src.tools.summarize_urls import SummarizeUrlsTool

  logger = ArtifactLogger()
  agent = MinimalAgent(
      tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
      logger=logger
  )

  result = agent.run("Check https://example.com")
  print(result)
  ```

### Listing 2.7: Running the Minimal Agent
- **File**: `scripts/example_01_minimal_agent.py`
- **Description**: Complete example of minimal agent execution
- **Demonstrates**:
  - Agent initialization
  - Tool orchestration
  - Artifact logging
  - Result interpretation
- **Run**: `python scripts/example_01_minimal_agent.py`
- **Note**: No API key required

## Safety Mechanisms

### Listing 2.8: Safety Gate Implementation
- **File**: `src/safety/gates.py`
- **Function**: `safety_gate(action: str, context: Dict) -> bool`
- **Features**:
  - Prohibited host filtering
  - Human confirmation prompt
  - Environment variable configuration
- **Usage**:
  ```python
  from src.safety.gates import safety_gate

  if safety_gate("ping", {"target": "example.com"}):
      perform_action()
  ```
- **Demo**: `scripts/example_02_safety_gate.py`

### Listing 2.10: Global Kill Switch
- **File**: `src/safety/kill_switch.py`
- **Description**: Emergency stop mechanism with background monitor
- **Classes**: `KillSwitch`
- **Key Methods**:
  - `start()`: Begin monitoring
  - `check()` / `.active`: Check if activated
  - `stop()`: Stop monitoring
- **Usage**:
  ```python
  from src.safety.kill_switch import KillSwitch

  with KillSwitch() as kill_switch:
      while not kill_switch.active:
          perform_action()
  ```

## NMAP Triage Workflow (Section 2.6)

### Listing 2.11: NMAP Output Format
- **File**: `data/nmap_output.txt`
- **Description**: Sample nmap scan output for triage examples
- **Format**:
  ```
  Host: api.example.com
    80/tcp    open  http    Apache httpd 2.4.41
    443/tcp   open  https   Apache httpd 2.4.41
    8443/tcp  open  https   Jetty 9.4.18

  Host: admin.example.com
    22/tcp    open  ssh     OpenSSH 7.2p2
    443/tcp   open  https   nginx 1.18.0
  ```

### Listing 2.12: Triage Report Output
- **Generated By**: `scripts/example_08_nmap_triage.py`
- **Description**: Prioritized triage summary
- **Format**:
  ```
  HIGH-INTEREST FINDINGS:

  1. legacy.example.com
     - Telnet (23/tcp) exposed publicly
     - Apache httpd 2.2.34 (end-of-life)
     Reason: Multiple legacy services on a public host

  MEDIUM-INTEREST FINDINGS:

  1. api.example.com
     - HTTPS service on 8443/tcp
     Reason: Non-standard admin or management interface

  LOWER-INTEREST FINDINGS:

  - admin.example.com
    - SSH (22/tcp) and HTTPS (443/tcp)
    Reason: Common service combination with no immediate anomalies
  ```

### NMAP Parser Tool
- **File**: `src/tools/nmap_parser.py`
- **Description**: Parses simplified nmap output into structured data
- **Classes**: `NmapParserTool`
- **Input**: Text from nmap scan
- **Output**: Structured host/service data
- **Usage**:
  ```python
  from src.tools.nmap_parser import NmapParserTool

  parser = NmapParserTool()
  result = parser.invoke({"text": nmap_output})

  for host in result["hosts"]:
      print(f"Host: {host['hostname']}")
      for svc in host["services"]:
          print(f"  Port {svc['port']}: {svc['service']}")
  ```

### Triage Analyzer Tool
- **File**: `src/tools/triage_analyzer.py`
- **Description**: Analyzes parsed nmap data and assigns priority scores
- **Classes**: `TriageAnalyzerTool`
- **Risk Indicators**:
  - Legacy services (telnet, FTP)
  - End-of-life software (Apache 2.2, old OpenSSH)
  - Non-standard ports (8080, 8443, 9090)
  - Odd service combinations
- **Scoring**:
  - Score ≥ 40: High priority
  - Score ≥ 15: Medium priority
  - Score < 15: Low priority
- **Usage**:
  ```python
  from src.tools.triage_analyzer import TriageAnalyzerTool

  analyzer = TriageAnalyzerTool()
  result = analyzer.invoke({"hosts": parsed_hosts})

  print(f"High priority: {result['summary']['high_count']}")
  for host in result['high_priority']:
      print(f"  - {host['hostname']} (score: {host['score']})")
  ```

### NMAP Triage Agent (Complete Workflow)
- **File**: `scripts/example_08_nmap_triage.py`
- **Description**: End-to-end triage workflow
- **Demonstrates**:
  - Reading saved nmap output (offline only)
  - Parsing reconnaissance data
  - Risk-based prioritization
  - Generating actionable reports
  - Complete artifact logging
- **Run**: `python scripts/example_08_nmap_triage.py`
- **Key Features**:
  - No network requests (offline analysis only)
  - Works on any scale (4 hosts or 4,000)
  - Explainable decisions
  - Human-readable output

## Example Scripts

### Example 1: Minimal Agent
- **File**: `scripts/example_01_minimal_agent.py`
- **Listing**: 2.7
- **Demonstrates**: Pure Python agent with URL tools
- **Run**: `python scripts/example_01_minimal_agent.py`
- **No API key required**

### Example 2: Safety Gates
- **File**: `scripts/example_02_safety_gate.py`
- **Listing**: 2.8 (demo)
- **Demonstrates**:
  - Prohibited host filtering
  - Human-in-the-loop confirmation
  - Safety-first design
- **Run**: `python scripts/example_02_safety_gate.py`
- **No API key required**

### Example 5: Artifact Logging
- **File**: `scripts/example_05_artifact_logging.py`
- **Listing**: 2.5 (demo)
- **Demonstrates**:
  - Structured logging workflow
  - JSONL format
  - Unique run IDs
- **Run**: `python scripts/example_05_artifact_logging.py`
- **No API key required**

### Example 8: NMAP Triage Agent
- **File**: `scripts/example_08_nmap_triage.py`
- **Listings**: 2.11, 2.12
- **Demonstrates**:
  - Complete triage workflow
  - NMAP parsing
  - Target prioritization
  - Report generation
- **Run**: `python scripts/example_08_nmap_triage.py`
- **No API key required**

## Data Files

### Sample NMAP Outputs
- **Files**:
  - `data/nmap_output.txt` - From Listing 2.11 (chapter example)
  - `data/nmap_output_clean.txt` - All modern services (low priority)
  - `data/nmap_output_mixed.txt` - Realistic pentest scenario
- **Description**: Sample reconnaissance data for triage examples
- **Schema**:
  ```
  Host: hostname.example.com
    port/proto  state  service  version string
  ```

## Navigation by Concept

### Agent Lifecycle
- **Minimal Implementation**: Listing 2.6 (`src/core/agent.py`)
- **Example Usage**: Listing 2.7 (`scripts/example_01_minimal_agent.py`)

### Data Structures
- **Core Models**: Listing 2.1 (`src/core/models.py`)
- **Tool Interface**: Listing 2.2 (`src/core/tool.py`)

### Tool Implementation
- **Base Class**: Listing 2.2 (`src/core/tool.py`)
- **URL Extractor**: Listing 2.3 (`src/tools/extract_urls.py`)
- **URL Summarizer**: Listing 2.4 (`src/tools/summarize_urls.py`)
- **NMAP Parser**: `src/tools/nmap_parser.py`
- **Triage Analyzer**: `src/tools/triage_analyzer.py`

### Safety & Control
- **Safety Gates**: Listing 2.8 (`src/safety/gates.py`)
- **Kill Switch**: Listing 2.10 (`src/safety/kill_switch.py`)
- **Demo**: `scripts/example_02_safety_gate.py`

### Logging & Audit
- **Logger Class**: Listing 2.5 (`src/core/logger.py`)
- **Record Format**: Listing 2.9 (`src/core/logger.py`)
- **Usage Example**: `scripts/example_05_artifact_logging.py`

### NMAP Triage
- **Input Format**: Listing 2.11 (`data/nmap_output.txt`)
- **Output Format**: Listing 2.12 (generated by triage agent)
- **Parser Tool**: `src/tools/nmap_parser.py`
- **Analyzer Tool**: `src/tools/triage_analyzer.py`
- **Complete Workflow**: `scripts/example_08_nmap_triage.py`

## Quick Reference by File Type

### Core Library (`src/core/`)
- `src/core/models.py` - Listing 2.1 (Message & Observation)
- `src/core/tool.py` - Listing 2.2 (Tool base class)
- `src/core/agent.py` - Listing 2.6 (MinimalAgent)
- `src/core/logger.py` - Listings 2.5, 2.9 (ArtifactLogger)

### Tools (`src/tools/`)
- `src/tools/extract_urls.py` - Listing 2.3
- `src/tools/summarize_urls.py` - Listing 2.4
- `src/tools/nmap_parser.py` - NMAP parser
- `src/tools/triage_analyzer.py` - Target prioritization

### Safety (`src/safety/`)
- `src/safety/gates.py` - Listing 2.8
- `src/safety/kill_switch.py` - Listing 2.10

### Example Scripts (`scripts/`)
- `scripts/example_01_minimal_agent.py` - Listing 2.7
- `scripts/example_02_safety_gate.py` - Safety demo
- `scripts/example_05_artifact_logging.py` - Logging demo
- `scripts/example_08_nmap_triage.py` - Triage workflow

### Data Files (`data/`)
- `data/nmap_output.txt` - Listing 2.11 (from chapter)
- `data/nmap_output_clean.txt` - Clean scan (low priority)
- `data/nmap_output_mixed.txt` - Realistic scenario

## Notes

- All source files include a header comment indicating their corresponding listing(s)
- All examples work without API keys (no LLM calls required)
- Examples 1, 2, 5, and 8 are framework-independent (pure Python)
- File paths are relative to the `chapters/ch02/` directory
- The focus is on learning agent mechanics, not framework abstractions

## Framework-Free Design

This chapter intentionally avoids AI frameworks to teach fundamentals:

- **No LangChain**: Learn agent patterns before framework abstractions
- **No AutoGen**: Understand multi-agent coordination from scratch
- **No LLM calls**: Focus on agent mechanics, not prompt engineering
- **Pure Python**: Portable, understandable, debuggable

Later chapters (3+) introduce frameworks once you understand how they work under the hood.
