"""
Visualization and auditing tools for multi-agent pipelines.

This module provides:
- Trace summarization (Listing 3.11)
- Mermaid diagram generation (Listing 3.12)
"""

from .trace import summarize_run, format_trace
from .mermaid import export_mermaid, generate_mermaid

__all__ = [
    "summarize_run",
    "format_trace",
    "export_mermaid",
    "generate_mermaid",
]
