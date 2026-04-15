# Chapter 2 — Listings Reference

| Listing | Description | File |
|---------|-------------|------|
| 2.1 | `Message` + `Observation` schemas | `src/core/models.py` |
| 2.2 | `Tool` abstract base class | `src/core/tool.py` |
| 2.3 | `ExtractUrlsTool` | `src/tools/extract_urls.py` |
| 2.4 | `SummarizeUrlsTool` | `src/tools/summarize_urls.py` |
| 2.5 | `ArtifactLogger` | `src/core/logger.py` |
| 2.6 | `MinimalAgent` | `src/core/agent.py` |
| 2.7 | Running the agent (demo) | `scripts/example_01_minimal_agent.py` |
| 2.8 | `safety_gate` function | `src/safety/gates.py` |
| 2.9 | Artifact record example | `scripts/example_05_artifact_logging.py` |
| 2.10 | `KillSwitch` | `src/safety/kill_switch.py` |
| 2.11 | nmap output (text sample) | `data/nmap_output.txt` |
| 2.12 | Triage summary (text sample) | Output of `scripts/example_08_nmap_triage.py` |

## Support code (not numbered listings)

The triage agent from Section 2.6 is implemented as runnable support code.
See `scripts/example_08_nmap_triage.py` for a complete end-to-end demonstration.

| File | Purpose |
|------|---------|
| `src/tools/nmap_parser.py` | `NmapParserTool` — parses nmap output into structured data |
| `src/tools/triage_analyzer.py` | `TriageAnalyzerTool` — risk-scores and prioritizes hosts |
| `scripts/example_08_nmap_triage.py` | End-to-end triage workflow |
