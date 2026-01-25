# Chapter 3: Multi-Agent Systems for Offensive Security Testing

Code companion for **Chapter 3** of *Black Hat AI: Offensive Security with Large Language Models*.

## Overview

This chapter introduces multi-agent pipeline architecture for coordinated offensive security operations. You'll learn:

- **Multi-Agent Design Patterns**: Sequential, parallel, branching, and event-driven pipelines
- **Artifact Management**: Structured state passing between agents
- **Pipeline Orchestration**: Centralized coordination of agent execution
- **Safety Gates**: Local and global governance controls
- **Resilience Patterns**: Retry logic, checkpointing, and alerting
- **Visualization**: Trace summarization and Mermaid diagrams

## Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# OR install with optional LangChain support
pip install -e .[langchain]

# OR install everything including dev tools
pip install -e .[all]
```

### 2. Run an Example

```bash
# Example 1: Basic sequential pipeline
python scripts/example_01_sequential.py

# Example 7: Complete Recon-Triage-Report capstone
python scripts/example_07_capstone.py
```

## Project Structure

```
ch03/
├── src/                        # Core library code
│   ├── core/                   # Fundamental components
│   │   ├── models.py           # Message & Observation classes
│   │   ├── artifact.py         # PipelineArtifact (Listing 3.2)
│   │   ├── logger.py           # Artifact logging
│   │   └── orchestrator.py     # PipelineOrchestrator (Listing 3.4)
│   ├── agents/                 # Pipeline stage implementations
│   │   ├── base.py             # Stage interface
│   │   ├── recon.py            # ReconAgent
│   │   ├── triage.py           # TriageAgent
│   │   └── report.py           # ReportAgent
│   ├── gates/                  # Safety gate implementations
│   │   ├── global_gate.py      # Time-based restrictions (Listing 3.6)
│   │   ├── scope_gate.py       # Authorized target filtering
│   │   ├── time_window_gate.py # Business hours enforcement
│   │   ├── approval_gate.py    # Human-in-the-loop
│   │   └── environment_gate.py # Production blocking (Listing 3.5)
│   ├── resilience/             # Error handling patterns
│   │   ├── retry.py            # Exponential backoff (Listing 3.8)
│   │   ├── checkpoint.py       # Resumable runs (Listing 3.9)
│   │   └── alerts.py           # Monitoring hooks (Listing 3.10)
│   ├── visualization/          # Audit and visualization
│   │   ├── trace.py            # Trace summarization (Listing 3.11)
│   │   └── mermaid.py          # Diagram generation (Listing 3.12)
│   └── adapters/               # LLM framework adapters
│       └── langchain/          # LangChain integration
├── scripts/                    # Runnable examples
├── data/                       # Sample datasets
├── tests/                      # Unit tests
├── docs/                       # Additional documentation
├── runs/                       # Artifact outputs (gitignored)
└── logs/                       # Runtime logs (gitignored)
```

## Finding Code Listings

Every source file includes a comment indicating which listing from the book it corresponds to.

| Listing | Description | File Location |
|---------|-------------|---------------|
| 3.1 | Exponential backoff | `src/resilience/retry.py` |
| 3.2 | Checkpointing | `src/resilience/checkpoint.py` |
| 3.3 | Error count hook | `src/resilience/alerts.py` |
| 3.4 | Trace summarization | `src/visualization/trace.py` |
| 3.5 | Mermaid flowchart generator | `src/visualization/mermaid.py` |
| 3.6 | ReconNormalizeAgent | `src/agents/recon_normalize.py` |
| 3.7 | TriageAgent | `src/agents/triage.py` |
| 3.8 | ReportAgent | `src/agents/report.py` |

See [`docs/listings_reference.md`](docs/listings_reference.md) for detailed listing reference.

## Running Examples

### Example 1: Basic Sequential Pipeline
```bash
python scripts/example_01_sequential.py
```
Demonstrates manual sequential execution of Recon → Triage → Report.

### Example 2: Pipeline Artifacts
```bash
python scripts/example_02_artifacts.py
```
Shows artifact creation, chaining, and JSONL logging.

### Example 3: Orchestrator
```bash
python scripts/example_03_orchestrator.py
```
Uses PipelineOrchestrator for automated stage execution with gates.

### Example 4: Gate Patterns
```bash
python scripts/example_04_gate_patterns.py
```
Demonstrates all five gate types and gate composition.

### Example 5: Resilience
```bash
python scripts/example_05_resilience.py
```
Shows retry with backoff, checkpointing, and alert hooks.

### Example 6: Visualization
```bash
python scripts/example_06_visualization.py
```
Generates trace summaries and Mermaid diagrams.

### Example 7: Capstone
```bash
python scripts/example_07_capstone.py
```
Complete pipeline with all components integrated.

## Using the Library

### Basic Pipeline

```python
from src.core.orchestrator import PipelineOrchestrator
from src.agents import ReconAgent, TriageAgent, ReportAgent
from src.gates import GlobalGate, EnvironmentGate

# Create agents
recon = ReconAgent(targets=["example.com"])
triage = TriageAgent(risk_threshold=5)
report = ReportAgent(output_dir="reports")

# Create gates
gates = [
    GlobalGate(start_hour=7, end_hour=22),
    EnvironmentGate(prohibited_patterns=["prod"]),
]

# Run pipeline
pipeline = PipelineOrchestrator(
    stages=[recon, triage, report],
    gates=gates,
)
result = pipeline.run()
```

### Custom Stage

```python
from src.agents.base import BaseStage
from src.core.artifact import PipelineArtifact

class MyStage(BaseStage):
    name = "my_stage"
    description = "Does something useful"

    def run(self, artifact):
        # Process input
        data = artifact.output if artifact else {}
        result = self.process(data)

        # Return artifact
        return PipelineArtifact.from_previous(
            previous=artifact,
            stage=self.name,
            output=result,
            success=True,
        )
```

### Custom Gate

```python
from src.gates.base import BaseGate

class MyGate(BaseGate):
    def allow(self, stage):
        # Custom logic
        if stage.name == "dangerous":
            return False
        return True
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

### Multi-Agent Design Patterns

| Pattern | Best For | Trade-offs |
|---------|----------|------------|
| Sequential | Prototypes, controlled tests | Slower on large data |
| Parallel | Large or diverse datasets | Complex merges |
| Branching | Adaptive logic | Harder to debug |
| Event-Driven | Continuous ops | Risk of runaway loops |

### Safety Gates

| Gate Type | Purpose |
|-----------|---------|
| GlobalGate | Time-based execution windows |
| ScopeGate | Authorized target filtering |
| TimeWindowGate | Business hours enforcement |
| ApprovalGate | Human confirmation required |
| EnvironmentGate | Production system blocking |

### Resilience Patterns

- **Retry with Backoff**: Handles transient failures gracefully
- **Checkpointing**: Enables resume without re-running completed stages
- **Alert Hooks**: Provides visibility into pipeline health

## Security Considerations

This code is designed for **authorized offensive security testing only**.

- Never run against systems you don't own or have permission to test
- Always configure appropriate safety gates
- Review artifacts and logs for unexpected behavior
- Keep API keys secure (never commit .env)
- Set `PROHIBITED_HOSTS` for your environment

## Additional Resources

- **Book**: *Black Hat AI* by [Authors]
- **LangChain Docs**: https://python.langchain.com/
- **Mermaid Docs**: https://mermaid.js.org/

## License

See the root LICENSE file.
