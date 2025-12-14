# Chapter 2: AI Agent Architecture

Code companion for **Chapter 2** of *Black Hat AI: Offensive Security with Large Language Models*.

## Overview

This chapter introduces the foundational architecture for AI-powered offensive security agents. You'll learn:

- **Message/Observation Pattern**: Core data structures for agent communication
- **Tool-Based Execution**: How agents interact with systems through tools
- **Plan-Act-Reflect Cycle**: The reasoning loop that drives agent behavior
- **Framework Adapters**: Integrating with LangChain and AutoGen
- **Safety Controls**: Human-in-the-loop gates and kill switches for responsible usage

## Quick Start

### 1. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# OR install with optional framework support
pip install -e .[langchain]  # LangChain support
pip install -e .[autogen]    # AutoGen support
pip install -e .[all]        # Everything including dev tools
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Run an Example

```bash
# Example 1: Basic agent with LangChain
python scripts/example_01_basic_agent.py

# Example 2: Safety gates demonstration
python scripts/example_02_safety_gate.py

# Example 5: Artifact logging (works without API key)
python scripts/example_05_artifact_logging.py
```

## Project Structure

```
ch02/
├── src/                    # Core library code
│   ├── core/               # Fundamental abstractions
│   │   ├── models.py       # Message & Observation classes
│   │   ├── tool.py         # Tool base class
│   │   ├── agent.py        # Agent interface (plan/act/reflect)
│   │   └── logger.py       # Artifact logging
│   ├── tools/              # Tool implementations
│   │   └── ping.py         # Network reachability tool
│   ├── adapters/           # Framework integrations
│   │   ├── langchain/      # LangChain adapter
│   │   ├── autogen/        # AutoGen adapter
│   │   └── selector.py     # Universal adapter selector
│   └── safety/             # Safety mechanisms
│       ├── gates.py        # Human-in-the-loop gates
│       └── kill_switch.py  # Emergency stop
├── scripts/                # Runnable examples
├── data/                   # Sample datasets
├── tests/                  # Unit tests
├── docs/                   # Additional documentation
├── logs/                   # Runtime logs
└── runs/                   # Artifact outputs

```

## Finding Code Listings

Every source file includes a comment indicating which listing from the book it corresponds to.

| Listing | Description | File Location |
|---------|-------------|---------------|
| 2.1 | Message & Observation models | `src/core/models.py` |
| 2.2 | Tool base class | `src/core/tool.py` |
| 2.3 | PingTool implementation | `src/tools/ping.py` |
| 2.4 | Agent interface (plan/act/reflect) | `src/core/agent.py` |
| 2.5 | Artifact logger | `src/core/logger.py` |
| 2.6 | LangChain agent adapter | `src/adapters/langchain/agent.py` |
| 2.7 | LangChain ping tool | `src/adapters/langchain/tools.py` |
| 2.8 | Agent execution example | `scripts/example_01_basic_agent.py` |
| 2.9 | Memory/reflection | `scripts/example_04_memory_buffer.py` |
| 2.10 | Safety gate | `src/safety/gates.py` + `scripts/example_02_safety_gate.py` |
| 2.11 | AutoGen example | `scripts/example_03_autogen.py` |
| 2.12 | AutoGen adapter | `src/adapters/autogen/agent.py` |
| 2.13 | Universal adapter selector | `src/adapters/selector.py` |
| 2.14 | Simple gate | `src/safety/gates.py` (simple_gate function) |
| 2.15 | Artifact logging example | `scripts/example_05_artifact_logging.py` |
| 2.16 | Global kill switch | `src/safety/kill_switch.py` |
| 2.17 | Planning/reasoning | `scripts/example_06_planning.py` |
| 2.18 | Reflection summary | `scripts/example_07_reflection.py` |

See [`docs/listings_reference.md`](docs/listings_reference.md) for more details.

## Running Examples

### Example 1: Basic Agent Execution
```bash
python scripts/example_01_basic_agent.py
```
Demonstrates LangChain agent with ping tool checking reachability of hosts.

### Example 2: Safety Gates
```bash
python scripts/example_02_safety_gate.py
```
Shows human-in-the-loop control with prohibited host filtering.

### Example 3: AutoGen Multi-Agent
```bash
python scripts/example_03_autogen.py
```
Multi-agent conversation using AutoGen framework.

### Example 4: Memory Buffer
```bash
python scripts/example_04_memory_buffer.py
```
Conversation memory and reflection patterns (no API key needed).

### Example 5: Artifact Logging
```bash
python scripts/example_05_artifact_logging.py
```
Structured audit logging to JSONL files (no API key needed).

### Example 6: Planning & Reasoning
```bash
python scripts/example_06_planning.py
```
Strategic triage and prioritization without taking actions.

### Example 7: Reflection Summary
```bash
python scripts/example_07_reflection.py
```
Generating summaries and identifying gaps in completed work.

## Using the Library in Your Code

### Basic Tool Usage

```python
from src.tools.ping import ping_host

result = ping_host("example.com")
print(f"Reachable: {result['reachable']}")
```

### Creating a LangChain Agent

```python
from src.adapters.langchain.agent import build_langchain_agent
from src.adapters.langchain.tools import ping_host_tool

agent = build_langchain_agent([ping_host_tool])
result = agent("Check if example.com is online")
print(result)
```

### Using Safety Gates

```python
from src.safety.gates import safety_gate
from src.tools.ping import ping_host

if safety_gate("ping", {"target": "example.com"}):
    result = ping_host("example.com")
    print(result)
```

### Artifact Logging

```python
from src.core.logger import ArtifactLogger

with ArtifactLogger() as logger:
    logger.write({"action": "scan", "target": "example.com"})
    # Logs written to runs/<uuid>.jsonl
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

### Message/Observation Pattern
- **Message**: Communication between components (user, agent, tool, system)
- **Observation**: Structured result from tool execution
- Enables clean separation of concerns and audit trails

### Plan-Act-Reflect Cycle
1. **Plan**: Analyze history, decide next action
2. **Act**: Execute action using tools
3. **Reflect**: Process results, update memory

### Safety-First Design
- **Safety Gates**: Human approval before dangerous actions
- **Prohibited Hosts**: Automatic blocking of production systems
- **Kill Switch**: Emergency stop for runaway agents
- **Audit Logging**: Complete record of all actions

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for detailed design documentation.

## Security Considerations

This code is designed for **authorized offensive security testing only**.

- Never run against systems you don't own or have permission to test
- Always use safety gates in production
- Review logs regularly for unexpected behavior
- Keep API keys secure (never commit .env)
- Set `PROHIBITED_HOSTS` environment variable for your environment

## Troubleshooting

### ImportError: No module named 'langchain'
```bash
pip install langchain langchain-openai
```

### ImportError: No module named 'autogen'
```bash
pip install pyautogen
```

### ValueError: OPENAI_API_KEY not set
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Permission denied when running examples
```bash
chmod +x scripts/*.py
```

## Additional Resources

- **Book**: *Black Hat AI* by [Authors]
- **LangChain Docs**: https://python.langchain.com/
- **AutoGen Docs**: https://microsoft.github.io/autogen/
- **OpenAI API**: https://platform.openai.com/docs

## License

See the root LICENSE file.

## Contributing

This is companion code for a book. For issues or suggestions, please open an issue on the main repository.
