# Chapter 2 Implementation Action Plan
**Created**: 2026-01-24
**Document Version**: ch2_v2.docx (version 2)
**Purpose**: Identify code to remove and code to add based on updated chapter content

---

## Executive Summary

After analyzing the new version of Chapter 2 (ch2_v2.docx) against the existing codebase, there are **SIGNIFICANT CHANGES**. The new version focuses on **framework-agnostic, pure Python implementation** and removes all LangChain/AutoGen framework examples from the main chapter content.

**Key Changes**:
- ❌ **REMOVE**: All LangChain and AutoGen example scripts and adapters
- ❌ **REMOVE**: PingTool (replaced with URL extraction tools)
- ✅ **ADD**: New minimal agent with URL extraction/summarization tools
- ✅ **ADD**: NMAP triage workflow
- ✅ **KEEP**: Core infrastructure (models, logger, safety gates, kill switch)

**Net Changes**:
- Removals: ~8 files (framework adapters, ping tool, framework examples)
- Additions: ~3 new files (URL tools, minimal agent, nmap triage)
- Updates: Core infrastructure remains

---

## Part A: Code to Remove

### Summary
❌ **MAJOR REMOVALS REQUIRED** - The chapter has been refocused on pure Python implementation

### Framework-Specific Code (REMOVE)

| Component | Status | Reason |
|-----------|--------|--------|
| `src/adapters/langchain/` (entire directory) | ❌ REMOVE | Not in v2 chapter |
| `src/adapters/autogen/` (entire directory) | ❌ REMOVE | Not in v2 chapter |
| `src/adapters/selector.py` | ❌ REMOVE | No framework selection needed |
| `src/adapters/__init__.py` | ⚠️ UPDATE | Remove framework imports |
| `scripts/example_01_basic_agent.py` | ❌ REMOVE | Uses LangChain |
| `scripts/example_03_autogen.py` | ❌ REMOVE | Uses AutoGen |
| `scripts/example_04_memory_buffer.py` | ❌ REMOVE | Uses LangChain memory |
| `scripts/example_06_planning.py` | ❌ REMOVE | Uses LangChain |
| `scripts/example_07_reflection.py` | ❌ REMOVE | Uses LangChain |

### Tool Implementations (REMOVE)

| Component | Status | Reason |
|-----------|--------|--------|
| `src/tools/ping.py` | ❌ REMOVE | Replaced with URL extraction tools |
| `tests/test_tools/test_ping.py` | ❌ REMOVE | No longer needed |

### Components to KEEP

| Component | Status | Chapter Reference |
|-----------|--------|-------------------|
| `src/core/models.py` | ✅ KEEP | Listing 2.1 (Message & Observation) |
| `src/core/tool.py` | ✅ KEEP | Listing 2.2 (Tool base class) |
| `src/core/logger.py` | ✅ KEEP | Listing 2.5 (ArtifactLogger) |
| `src/core/agent.py` | ⚠️ UPDATE | Modify for minimal agent pattern |
| `src/safety/gates.py` | ✅ KEEP | Listing 2.8 (Safety gates) |
| `src/safety/kill_switch.py` | ✅ KEEP | Listing 2.10 (Kill switch) |
| `scripts/example_02_safety_gate.py` | ✅ KEEP | Still relevant |
| `scripts/example_05_artifact_logging.py` | ✅ KEEP | Still relevant |
| `data/targets.py` | ⚠️ UPDATE | Repurpose for NMAP data |

### Detailed Removal Instructions

#### Step 1: Remove Framework Adapter Directories
```bash
rm -rf src/adapters/langchain/
rm -rf src/adapters/autogen/
rm src/adapters/selector.py
```

#### Step 2: Remove Framework-Dependent Example Scripts
```bash
rm scripts/example_01_basic_agent.py
rm scripts/example_03_autogen.py
rm scripts/example_04_memory_buffer.py
rm scripts/example_06_planning.py
rm scripts/example_07_reflection.py
```

#### Step 3: Remove PingTool and Related Tests
```bash
rm src/tools/ping.py
rm tests/test_tools/test_ping.py
```

#### Step 4: Clean Up Test Directories
```bash
rm -rf tests/test_adapters/
```

### Impact Analysis

**Removed Files**: 13 files + 2 directories
**Lines of Code Removed**: ~1,500-2,000 LOC
**Dependencies No Longer Needed**:
- `langchain`
- `langchain-openai`
- `pyautogen`

**Risk**: LOW - All removed code is framework-specific and not used in v2 chapter

---

## Part B: Code to Add

### Summary
The new chapter v2 introduces **framework-agnostic pure Python implementation** with new tools and workflows:

1. **URL Extraction Tools** - ExtractUrlsTool and SummarizeUrlsTool (Section 2.4)
2. **MinimalAgent** - Pure Python agent implementation (Section 2.4)
3. **NMAP Triage Agent** - Workflow for triaging reconnaissance data (Section 2.6)
4. **Sample NMAP Data** - Realistic nmap output for examples

---

### 1. URL Extraction and Summarization Tools

**Priority**: 🔴 HIGH
**Chapter Reference**: Section 2.4.3 and 2.4.4 (Listings 2.3 and 2.4)
**Files to Create**:
- `src/tools/extract_urls.py` (NEW)
- `src/tools/summarize_urls.py` (NEW)

#### Description
Two simple tools that demonstrate the minimal agent pattern. The first extracts URLs from text using regex, the second summarizes the results.

#### Requirements from Chapter

**Listing 2.3 - ExtractUrlsTool**:
```python
import re

class ExtractUrlsTool(Tool):
    name = "extract_urls"

    def invoke(self, input: dict) -> dict:
        urls = re.findall(r"https?://[^\s]+", input["text"])
        return {"urls": urls}
```

**Listing 2.4 - SummarizeUrlsTool**:
```python
class SummarizeUrlsTool(Tool):
    name = "summarize_urls"

    def invoke(self, input: dict) -> dict:
        return {
            "count": len(input["urls"]),
            "summary": f"Found {len(input['urls'])} URLs."
        }
```

#### Implementation Notes
- Both inherit from the existing `Tool` base class
- No external dependencies (use standard library only)
- Should follow existing code style
- Include docstrings and type hints

---

### 2. Minimal Agent Implementation

**Priority**: 🔴 HIGH
**Chapter Reference**: Section 2.4.6 (Listing 2.6)
**File to Create/Update**: `src/core/agent.py` (UPDATE)

#### Description
A minimal, pure Python agent that orchestrates two tools in sequence without any framework dependencies.

#### Requirements from Chapter

**Listing 2.6 - MinimalAgent**:
```python
class MinimalAgent:
    def __init__(self, tools, logger):
        self.tools = {tool.name: tool for tool in tools}
        self.logger = logger

    def run(self, text: str):
        # Step 1: Extract URLs
        plan = "extract_urls"
        observation_1 = self.tools[plan].invoke({"text": text})
        self.logger.write({
            "tool": plan,
            "input": {"text": text},
            "output": observation_1
        })

        # Step 2: Summarize URLs
        plan = "summarize_urls"
        observation_2 = self.tools[plan].invoke(observation_1)
        self.logger.write({
            "tool": plan,
            "input": observation_1,
            "output": observation_2
        })

        return observation_2
```

#### Implementation Notes
- Add `MinimalAgent` class to existing `src/core/agent.py`
- Keep existing `Agent` base class (if any)
- No LLM calls - pure orchestration logic
- Uses existing `ArtifactLogger`
- Explicit, sequential execution (no loops)

---

### 3. Minimal Agent Example Script

**Priority**: 🔴 HIGH
**Chapter Reference**: Section 2.4.7 (Listing 2.7)
**File to Create**: `scripts/example_01_minimal_agent.py` (REPLACE existing example_01)

#### Description
Demonstrates the minimal agent running the URL extraction workflow.

#### Requirements from Chapter

**Listing 2.7 - Running the agent**:
```python
logger = ArtifactLogger()
agent = MinimalAgent(
    tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
    logger=logger
)

result = agent.run(
    "Check https://example.com and https://admin.example.com/login"
)
print(result)
```

#### Full Implementation

```python
#!/usr/bin/env python3
"""
Minimal Agent Example

From Listing 2.7 in Black Hat AI Chapter 2.

Demonstrates:
- Pure Python agent implementation (no frameworks)
- Sequential tool execution
- Artifact logging
- Explicit decision-making
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.logger import ArtifactLogger
from src.core.agent import MinimalAgent
from src.tools.extract_urls import ExtractUrlsTool
from src.tools.summarize_urls import SummarizeUrlsTool


def main():
    """Run minimal agent demonstration."""
    print("=" * 60)
    print("Example 1: Minimal Agent")
    print("=" * 60)
    print()

    # Create logger
    logger = ArtifactLogger()

    # Create agent with two tools
    agent = MinimalAgent(
        tools=[ExtractUrlsTool(), SummarizeUrlsTool()],
        logger=logger
    )

    # Run agent
    test_input = "Check https://example.com and https://admin.example.com/login"
    print(f"Input: {test_input}")
    print()

    result = agent.run(test_input)

    print("Result:")
    print(f"  Count: {result['count']}")
    print(f"  Summary: {result['summary']}")
    print()
    print("=" * 60)
    print("Check runs/ directory for artifact logs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### 4. NMAP Triage Agent

**Priority**: 🟡 MEDIUM
**Chapter Reference**: Section 2.6 (The Triage Agent)
**File to Create**: `scripts/example_08_nmap_triage.py` (NEW)

#### Description
A practical agent that reads nmap scan output and produces a prioritized list of interesting targets.

#### Requirements from Chapter

**Section 2.6.1 - What is triage?**
- Agent works on SAVED output files (never scans)
- Reviews recon results and helps decide where to focus
- Reduces noise and surfaces signals

**Section 2.6.2 - NMAP output** (Listing 2.11):
```
Host: api.example.com
  80/tcp    open  http    Apache httpd 2.4.41
  443/tcp   open  https   Apache httpd 2.4.41
  8443/tcp  open  https   Jetty 9.4.18

Host: admin.example.com
  22/tcp    open  ssh     OpenSSH 7.2p2
  443/tcp   open  https   nginx 1.18.0

Host: files.example.com
  21/tcp    open  ftp     vsftpd 3.0.3
  80/tcp    open  http    nginx 1.14.2

Host: legacy.example.com
  23/tcp    open  telnet
  80/tcp    open  http    Apache httpd 2.2.34
```

**Section 2.6.3 - Agent decision scope**:
- Flag unusual exposure (non-standard ports)
- Spot odd combinations (FTP + web server)
- Group similar hosts
- Surface red flags (telnet, end-of-life software)

**Section 2.6.4 - Triage artifacts** (Listing 2.12):
```
High-interest findings:
1. legacy.example.com
   - Telnet (23/tcp) exposed publicly
   - Apache httpd 2.2.34 (end-of-life)
   Reason: Multiple legacy services on a public host

2. files.example.com
   - FTP (21/tcp) exposed alongside HTTP
   Reason: Public FTP service paired with web server

3. api.example.com
   - HTTPS service on 8443/tcp (Jetty 9.4.18)
   Reason: Non-standard admin or management interface

Lower-interest findings:
- admin.example.com
  - SSH (22/tcp) and HTTPS (443/tcp)
  Reason: Common service combination with no immediate anomalies
```

#### Implementation Approach

**Phase 1: NMAP Parser Tool**
```python
# src/tools/nmap_parser.py
class NmapParserTool(Tool):
    """Parse simplified nmap output into structured data."""
    name = "parse_nmap"

    def invoke(self, input: dict) -> dict:
        """
        Parse nmap text output.

        Input: {"text": "Host: example.com\\n  80/tcp open http..."}
        Output: {
            "hosts": [
                {
                    "hostname": "example.com",
                    "services": [
                        {"port": 80, "proto": "tcp", "state": "open",
                         "service": "http", "version": "Apache httpd 2.4.41"}
                    ]
                }
            ]
        }
        """
        # Implementation here
```

**Phase 2: Triage Analysis Tool**
```python
# src/tools/triage_analyzer.py
class TriageAnalyzerTool(Tool):
    """Analyze parsed nmap data and prioritize targets."""
    name = "analyze_triage"

    def invoke(self, input: dict) -> dict:
        """
        Analyze hosts and assign priority scores.

        Input: {"hosts": [...]}
        Output: {
            "high_priority": [...],
            "medium_priority": [...],
            "low_priority": [...]
        }
        """
        # Scoring logic:
        # - Telnet/FTP = HIGH
        # - End-of-life software = HIGH
        # - Non-standard ports (8080, 8443, etc) = MEDIUM
        # - Odd combinations = MEDIUM
        # - Standard web stack = LOW
```

**Phase 3: Triage Agent**
```python
# scripts/example_08_nmap_triage.py
class NmapTriageAgent:
    """Agent for triaging nmap reconnaissance data."""

    def __init__(self, logger):
        self.tools = {
            "parse_nmap": NmapParserTool(),
            "analyze_triage": TriageAnalyzerTool()
        }
        self.logger = logger

    def run(self, nmap_output: str):
        # Parse nmap output
        parsed = self.tools["parse_nmap"].invoke({"text": nmap_output})
        self.logger.write({"stage": "parse", "output": parsed})

        # Analyze and prioritize
        analysis = self.tools["analyze_triage"].invoke(parsed)
        self.logger.write({"stage": "analyze", "output": analysis})

        # Generate report
        report = self._generate_report(analysis)
        self.logger.write({"stage": "report", "output": report})

        return report

    def _generate_report(self, analysis):
        # Format as shown in Listing 2.12
        ...
```

---

### 5. Sample NMAP Data

**Priority**: 🟡 MEDIUM
**Chapter Reference**: Section 2.6.2 (Listing 2.11)
**File to Create**: `data/nmap_output.txt` (NEW)

#### Description
Sample nmap scan output for testing the triage agent.

#### Content (from Chapter)
```
Host: api.example.com
  80/tcp    open  http    Apache httpd 2.4.41
  443/tcp   open  https   Apache httpd 2.4.41
  8443/tcp  open  https   Jetty 9.4.18

Host: admin.example.com
  22/tcp    open  ssh     OpenSSH 7.2p2
  443/tcp   open  https   nginx 1.18.0

Host: files.example.com
  21/tcp    open  ftp     vsftpd 3.0.3
  80/tcp    open  http    nginx 1.14.2

Host: legacy.example.com
  23/tcp    open  telnet
  80/tcp    open  http    Apache httpd 2.2.34
```

#### Additional Samples
Create 2-3 additional sample files with different scenarios:
- `data/nmap_output_large.txt` - Larger scope with more noise
- `data/nmap_output_clean.txt` - No red flags (all modern services)
- `data/nmap_output_mixed.txt` - Mix of high/medium/low priority

---

### 6. Documentation Updates

**Priority**: 🟡 MEDIUM
**Files to Update**:
- `README.md`
- `docs/listings_reference.md`
- `requirements.txt` (remove framework dependencies)

#### README.md Updates

**Replace "Framework Adapters" section with**:
```markdown
## Pure Python Implementation

This chapter uses **pure Python** with no AI framework dependencies. The focus is on understanding agent mechanics, not framework abstractions.

### Why No Frameworks?

- **Clarity**: See exactly how agents work without framework magic
- **Portability**: Code runs anywhere Python runs
- **Educational**: Learn core concepts that transfer to any framework
- **Simplicity**: Fewer dependencies, faster setup
```

**Update Example Listings**:
```markdown
### Example 1: Minimal Agent
```bash
python scripts/example_01_minimal_agent.py
```
Demonstrates pure Python agent with URL extraction tools.

### Example 2: Safety Gates
```bash
python scripts/example_02_safety_gate.py
```
Human-in-the-loop control (no API key required).

### Example 5: Artifact Logging
```bash
python scripts/example_05_artifact_logging.py
```
Structured audit logging (no API key required).

### Example 8: NMAP Triage
```bash
python scripts/example_08_nmap_triage.py
```
Triage reconnaissance data and prioritize targets.
```

#### listings_reference.md Updates

**Replace with new mappings**:
```markdown
| Listing | Description | File Location |
|---------|-------------|---------------|
| 2.1 | Message & Observation models | `src/core/models.py` |
| 2.2 | Tool base class | `src/core/tool.py` |
| 2.3 | ExtractUrlsTool | `src/tools/extract_urls.py` |
| 2.4 | SummarizeUrlsTool | `src/tools/summarize_urls.py` |
| 2.5 | Artifact logger | `src/core/logger.py` |
| 2.6 | MinimalAgent | `src/core/agent.py` |
| 2.7 | Running the agent | `scripts/example_01_minimal_agent.py` |
| 2.8 | Safety gate | `src/safety/gates.py` |
| 2.9 | Artifact record | `src/core/logger.py` |
| 2.10 | Kill switch | `src/safety/kill_switch.py` |
| 2.11 | NMAP output | `data/nmap_output.txt` |
| 2.12 | Triage output | `scripts/example_08_nmap_triage.py` |
```

#### requirements.txt Updates

**Remove**:
```
langchain
langchain-openai
pyautogen
```

**Keep**:
```
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## Implementation Priority Matrix

| Component | Priority | Effort | Dependencies | Timeline |
|-----------|----------|--------|--------------|----------|
| Remove framework code | 🔴 HIGH | 30 min | None | Day 1 |
| URL extraction tools | 🔴 HIGH | 1 hour | Tool base class | Day 1 |
| MinimalAgent | 🔴 HIGH | 1 hour | URL tools, logger | Day 1 |
| Minimal agent example | 🔴 HIGH | 30 min | MinimalAgent | Day 1 |
| NMAP parser tool | 🟡 MEDIUM | 2 hours | Tool base class | Day 2 |
| Triage analyzer tool | 🟡 MEDIUM | 2 hours | NMAP parser | Day 2 |
| NMAP triage agent/script | 🟡 MEDIUM | 2 hours | Triage tools | Day 2 |
| Sample NMAP data | 🟡 MEDIUM | 1 hour | None | Day 2 |
| Documentation updates | 🟡 MEDIUM | 1 hour | All above | Day 3 |

**Total Estimated Effort**: 11 hours
**Recommended Timeline**: 2-3 days

---

## Implementation Sequence

### Day 1: Clean Up and Core Tools
1. ✅ **Remove framework code** (30 min)
   - Delete LangChain/AutoGen adapters
   - Delete framework-dependent examples
   - Update requirements.txt

2. ✅ **Implement URL tools** (1 hour)
   - `src/tools/extract_urls.py`
   - `src/tools/summarize_urls.py`
   - Basic tests

3. ✅ **Implement MinimalAgent** (1 hour)
   - Add to `src/core/agent.py`
   - Test with URL tools
   - Verify artifact logging

4. ✅ **Create minimal agent example** (30 min)
   - `scripts/example_01_minimal_agent.py`
   - Test end-to-end
   - Verify output matches chapter

### Day 2: NMAP Triage Workflow
5. ✅ **Implement NMAP parser** (2 hours)
   - `src/tools/nmap_parser.py`
   - Parse chapter format
   - Handle edge cases
   - Tests

6. ✅ **Implement triage analyzer** (2 hours)
   - `src/tools/triage_analyzer.py`
   - Scoring logic
   - Priority classification
   - Tests

7. ✅ **Create NMAP triage agent** (2 hours)
   - `scripts/example_08_nmap_triage.py`
   - Integrate parser + analyzer
   - Generate reports
   - Test with sample data

8. ✅ **Create sample NMAP data** (1 hour)
   - `data/nmap_output.txt` (from chapter)
   - Additional test scenarios

### Day 3: Documentation and Polish
9. ✅ **Update documentation** (1 hour)
   - Update README.md
   - Update listings_reference.md
   - Add usage examples

10. ✅ **Final verification** (30 min)
    - Run all examples
    - Verify artifact logging
    - Check safety controls
    - Cross-reference with chapter

---

## File Structure After Implementation

```
chapters/ch02/
├── src/
│   ├── core/
│   │   ├── models.py              # KEEP (Listing 2.1)
│   │   ├── tool.py                # KEEP (Listing 2.2)
│   │   ├── logger.py              # KEEP (Listing 2.5)
│   │   └── agent.py               # UPDATE (add MinimalAgent - Listing 2.6)
│   ├── tools/
│   │   ├── extract_urls.py        # NEW ✨ (Listing 2.3)
│   │   ├── summarize_urls.py      # NEW ✨ (Listing 2.4)
│   │   ├── nmap_parser.py         # NEW ✨
│   │   └── triage_analyzer.py     # NEW ✨
│   ├── safety/
│   │   ├── gates.py               # KEEP (Listing 2.8)
│   │   └── kill_switch.py         # KEEP (Listing 2.10)
│   └── adapters/                  # DELETE entire directory ❌
├── scripts/
│   ├── example_01_minimal_agent.py    # NEW ✨ (Listing 2.7)
│   ├── example_02_safety_gate.py      # KEEP
│   ├── example_05_artifact_logging.py # KEEP
│   └── example_08_nmap_triage.py      # NEW ✨
├── data/
│   ├── nmap_output.txt            # NEW ✨ (Listing 2.11)
│   ├── nmap_output_large.txt      # NEW ✨
│   └── targets.py                 # UPDATE (repurpose or keep for legacy)
├── tests/
│   ├── test_core/                 # KEEP (update as needed)
│   ├── test_safety/               # KEEP
│   └── test_tools/
│       ├── test_extract_urls.py   # NEW ✨
│       ├── test_summarize_urls.py # NEW ✨
│       ├── test_nmap_parser.py    # NEW ✨
│       └── test_triage_analyzer.py# NEW ✨
└── docs/
    ├── listings_reference.md      # UPDATE 📝
    └── ch2_action_plan.md         # This file

README.md                          # UPDATE 📝
requirements.txt                   # UPDATE 📝 (remove frameworks)
```

---

## Validation Checklist

### Code Removal
- [ ] All LangChain code removed
- [ ] All AutoGen code removed
- [ ] PingTool removed
- [ ] Framework-dependent examples removed
- [ ] Test files cleaned up
- [ ] No broken imports remain

### New Implementations
- [ ] ExtractUrlsTool works correctly
- [ ] SummarizeUrlsTool works correctly
- [ ] MinimalAgent orchestrates tools
- [ ] Minimal agent example runs
- [ ] NMAP parser handles chapter format
- [ ] Triage analyzer produces correct priorities
- [ ] NMAP triage agent generates reports
- [ ] Sample NMAP data is realistic

### Code Quality
- [ ] All code follows existing style
- [ ] Docstrings added
- [ ] Type hints used
- [ ] Error handling included
- [ ] No hardcoded values

### Testing
- [ ] Unit tests for URL tools
- [ ] Unit tests for NMAP tools
- [ ] Integration test for minimal agent
- [ ] Integration test for triage agent
- [ ] All tests pass

### Chapter Alignment
- [ ] Code matches Listing 2.3 (ExtractUrlsTool)
- [ ] Code matches Listing 2.4 (SummarizeUrlsTool)
- [ ] Code matches Listing 2.6 (MinimalAgent)
- [ ] Code matches Listing 2.7 (Running the agent)
- [ ] NMAP data matches Listing 2.11
- [ ] Triage output matches Listing 2.12
- [ ] Example outputs match chapter

### Documentation
- [ ] README.md updated (no frameworks)
- [ ] listings_reference.md updated
- [ ] requirements.txt updated
- [ ] Usage examples clear
- [ ] File headers indicate listings

---

## Risk Assessment

### Low Risk
- ✅ Core infrastructure unchanged (models, logger, safety)
- ✅ New tools are simple (no external dependencies)
- ✅ Can develop incrementally

### Medium Risk
- ⚠️ Large code removal (framework adapters)
  - **Mitigation**: Commit to git before removal, can recover if needed

- ⚠️ Changing example scripts users may reference
  - **Mitigation**: Keep example_02 and example_05 unchanged

### Potential Issues
- ⚠️ NMAP parsing complexity (many format variations)
  - **Mitigation**: Support only the simplified format from chapter

- ⚠️ Triage scoring may be subjective
  - **Mitigation**: Document scoring rules clearly, allow customization

---

## Success Metrics

Implementation is successful when:

1. **Removal Complete**: No framework code remains in codebase
2. **Minimal Agent Works**: URL extraction example runs correctly
3. **NMAP Triage Works**: Produces output matching Listing 2.12
4. **No Dependencies**: Runs with only pydantic and python-dotenv
5. **Tests Pass**: All unit and integration tests pass
6. **Documentation Accurate**: README and listings match reality
7. **Chapter Aligned**: All code matches chapter listings exactly

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Backup current code** (git commit/branch)
3. **Begin Day 1 tasks** (removals and URL tools)
4. **Implement Day 2 tasks** (NMAP triage)
5. **Polish and document** (Day 3)
6. **Validate against chapter** before considering complete

---

## Appendix: Chapter v2 Section Mapping

| Chapter Section | Implementation Component |
|-----------------|--------------------------|
| 2.1 Limitations of script-based automation | Conceptual (no code) |
| 2.2 What is an agent? | Conceptual (no code) |
| 2.3 Anatomy of an agent | `src/core/models.py`, `src/core/tool.py` |
| 2.4 Building the minimal agent | URL tools, MinimalAgent, example_01 |
| 2.5 Safety and governance | `src/safety/*`, example_02 |
| 2.6 The triage agent | NMAP tools, triage agent, example_08 |

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2026-01-24
**Prepared By**: Claude Code Analysis
**Next Review**: After implementation completion
