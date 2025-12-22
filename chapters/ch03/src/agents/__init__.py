"""
Multi-agent pipeline stages for offensive security.

This module provides specialized agents for the Recon-Triage-Report workflow:
- ReconAgent: Discovers targets and gathers information
- TriageAgent: Scores and prioritizes findings by risk
- ReportAgent: Generates human-readable summaries
"""

from .base import BaseStage
from .recon import ReconAgent
from .triage import TriageAgent
from .report import ReportAgent

__all__ = [
    "BaseStage",
    "ReconAgent",
    "TriageAgent",
    "ReportAgent",
]
