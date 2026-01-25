"""
Multi-agent pipeline stages for offensive security.

This module provides specialized agents for the Recon-Triage-Report workflow:
- ReconAgent: Discovers targets and gathers raw information
- ReconNormalizeAgent: Normalizes raw recon data into structured schema
- TriageAgent: Scores and prioritizes findings by risk
- ReportAgent: Generates human-readable summaries
"""

from .base import BaseStage
from .recon import ReconAgent
from .recon_normalize import ReconNormalizeAgent
from .triage import TriageAgent
from .report import ReportAgent

__all__ = [
    "BaseStage",
    "ReconAgent",
    "ReconNormalizeAgent",
    "TriageAgent",
    "ReportAgent",
]
