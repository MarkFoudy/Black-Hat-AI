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

### Listing 2.4: Agent Interface
- **File**: `src/core/agent.py`
- **Description**: Plan-Act-Reflect cycle implementation
- **Classes**: `Agent`
- **Key Methods**:
  - `plan(history) -> Message`: Decide next action
  - `act(plan, tools) -> Observation`: Execute action
  - `reflect(observation) -> Message`: Update memory
- **Usage**: Subclass `Agent` and implement lifecycle methods

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

## Tools

### Listing 2.3: PingTool Implementation
- **File**: `src/tools/ping.py`
- **Description**: Network reachability testing via ICMP ping
- **Classes**: `PingTool`
- **Functions**: `ping_host(host: str) -> Dict`
- **Usage**:
  ```python
  from src.tools.ping import ping_host
  result = ping_host("example.com")
  ```

### Listing 2.7: LangChain Ping Tool
- **File**: `src/adapters/langchain/tools.py`
- **Description**: LangChain-compatible ping tool wrapper
- **Functions**: `ping_host(host: str) -> str`
- **Exports**: `ping_host_tool` (decorated version)
- **Usage**: Pass `ping_host_tool` to LangChain agents

## Framework Adapters

### Listing 2.6: LangChain Agent Adapter
- **File**: `src/adapters/langchain/agent.py`
- **Description**: Factory for creating LangChain agents with logging
- **Functions**: `build_langchain_agent(tools: List[Tool]) -> Callable`
- **Requirements**: LangChain, OpenAI API key
- **Features**:
  - OpenAI LLM backend
  - Conversation memory
  - Automatic artifact logging
  - Verbose output
- **Usage**:
  ```python
  from src.adapters.langchain.agent import build_langchain_agent
  agent = build_langchain_agent([ping_host_tool])
  result = agent("Check if example.com is online")
  ```

### Listing 2.12: AutoGen Adapter
- **File**: `src/adapters/autogen/agent.py`
- **Description**: Factory for creating AutoGen multi-agent systems
- **Functions**: `build_autogen_agent() -> Callable`
- **Requirements**: AutoGen, OpenAI API key
- **Agents**:
  - `AssistantAgent`: AI-powered reasoning
  - `UserProxyAgent`: Human operator proxy
- **Features**:
  - Multi-agent conversation
  - Automatic artifact logging
  - Code execution disabled (security)
- **Usage**:
  ```python
  from src.adapters.autogen.agent import build_autogen_agent
  agent = build_autogen_agent()
  result = agent("Check reachability of example.com")
  ```

### Listing 2.13: Universal Adapter Selector
- **File**: `src/adapters/selector.py`
- **Description**: Runtime selection between frameworks
- **Functions**:
  - `get_agent(adapter: str, tools: List) -> Callable`
  - `list_available_adapters() -> List[str]`
- **Supported Adapters**: `"langchain"`, `"autogen"`
- **Usage**:
  ```python
  from src.adapters.selector import get_agent
  agent = get_agent(adapter="langchain", tools=[ping_tool])
  ```

## Safety Mechanisms

### Listing 2.10: Safety Gate (Full Version)
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

### Listing 2.14: Simple Gate
- **File**: `src/safety/gates.py`
- **Function**: `simple_gate(action: str, context: Dict) -> bool`
- **Features**: Human confirmation only (no filtering)
- **Usage**: Same as safety_gate but simpler

### Listing 2.16: Global Kill Switch
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

## Example Scripts

### Listing 2.8: Basic Agent Execution
- **File**: `scripts/example_01_basic_agent.py`
- **Demonstrates**: LangChain agent with ping tool
- **Run**: `python scripts/example_01_basic_agent.py`

### Listing 2.9: Memory & Reflection
- **File**: `scripts/example_04_memory_buffer.py`
- **Demonstrates**: LangChain conversation memory usage
- **Run**: `python scripts/example_04_memory_buffer.py`
- **Note**: No API key required

### Listing 2.11: AutoGen Example
- **File**: `scripts/example_03_autogen.py`
- **Demonstrates**: AutoGen multi-agent system
- **Run**: `python scripts/example_03_autogen.py`

### Listing 2.15: Artifact Logging Example
- **File**: `scripts/example_05_artifact_logging.py`
- **Demonstrates**: Structured audit logging workflow
- **Run**: `python scripts/example_05_artifact_logging.py`
- **Note**: No API key required

### Listing 2.17: Planning & Reasoning
- **File**: `scripts/example_06_planning.py`
- **Demonstrates**: Strategic triage without execution
- **Run**: `python scripts/example_06_planning.py`

### Listing 2.18: Reflection Summary
- **File**: `scripts/example_07_reflection.py`
- **Demonstrates**: Generating summaries and identifying gaps
- **Run**: `python scripts/example_07_reflection.py`

## Additional Examples

### Safety Gate Demo
- **File**: `scripts/example_02_safety_gate.py`
- **Demonstrates**:
  - Prohibited host filtering
  - Human-in-the-loop confirmation
  - Simple vs. full safety gates
- **Run**: `python scripts/example_02_safety_gate.py`
- **Note**: No API key required

## Data Files

### Sample Targets
- **File**: `data/targets.py`
- **Description**: Sample hostnames and IPs for examples
- **Exports**:
  - `targets`: List of sample hosts
  - `high_value_targets`: Priority targets
  - `target_metadata`: Additional context
- **Usage**: `from data.targets import targets`

## Navigation by Concept

### Agent Lifecycle
- **Interface**: Listing 2.4 (`src/core/agent.py`)
- **LangChain Implementation**: Listing 2.6 (`src/adapters/langchain/agent.py`)
- **AutoGen Implementation**: Listing 2.12 (`src/adapters/autogen/agent.py`)

### Data Structures
- **Core Models**: Listing 2.1 (`src/core/models.py`)
- **Tool Interface**: Listing 2.2 (`src/core/tool.py`)

### Tool Implementation
- **Base Class**: Listing 2.2 (`src/core/tool.py`)
- **Concrete Example**: Listing 2.3 (`src/tools/ping.py`)
- **LangChain Wrapper**: Listing 2.7 (`src/adapters/langchain/tools.py`)

### Safety & Control
- **Safety Gates**: Listings 2.10, 2.14 (`src/safety/gates.py`)
- **Kill Switch**: Listing 2.16 (`src/safety/kill_switch.py`)
- **Demo**: `scripts/example_02_safety_gate.py`

### Logging & Audit
- **Logger Class**: Listing 2.5 (`src/core/logger.py`)
- **Usage Example**: Listing 2.15 (`scripts/example_05_artifact_logging.py`)

### Memory & Reflection
- **Memory Demo**: Listing 2.9 (`scripts/example_04_memory_buffer.py`)
- **Reflection Demo**: Listing 2.18 (`scripts/example_07_reflection.py`)

## Quick Reference by File Type

### Core Library (`src/`)
- `src/core/models.py` - Listing 2.1
- `src/core/tool.py` - Listing 2.2
- `src/core/agent.py` - Listing 2.4
- `src/core/logger.py` - Listing 2.5
- `src/tools/ping.py` - Listing 2.3
- `src/adapters/langchain/agent.py` - Listing 2.6
- `src/adapters/langchain/tools.py` - Listing 2.7
- `src/adapters/autogen/agent.py` - Listing 2.12
- `src/adapters/selector.py` - Listing 2.13
- `src/safety/gates.py` - Listings 2.10, 2.14
- `src/safety/kill_switch.py` - Listing 2.16

### Example Scripts (`scripts/`)
- `scripts/example_01_basic_agent.py` - Listing 2.8
- `scripts/example_03_autogen.py` - Listing 2.11
- `scripts/example_04_memory_buffer.py` - Listing 2.9
- `scripts/example_05_artifact_logging.py` - Listing 2.15
- `scripts/example_06_planning.py` - Listing 2.17
- `scripts/example_07_reflection.py` - Listing 2.18

### Data Files
- `data/targets.py` - Sample data (referenced in Listings 2.17, 2.18)

## Notes

- All source files include a header comment indicating their corresponding listing(s)
- Examples 2, 4, and 5 can run without an OpenAI API key
- Examples 1, 3, 6, and 7 require `OPENAI_API_KEY` environment variable
- File paths are relative to the `chapters/ch02/` directory
