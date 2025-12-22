"""
Core components for multi-agent pipeline orchestration.

This module provides:
- Data models (Message, Observation)
- Pipeline artifacts for state management
- Artifact logging for audit trails
- Pipeline orchestrator for coordinating agents
"""

from .models import Message, Observation
from .artifact import PipelineArtifact
from .logger import ArtifactLogger
from .orchestrator import PipelineOrchestrator

__all__ = [
    "Message",
    "Observation",
    "PipelineArtifact",
    "ArtifactLogger",
    "PipelineOrchestrator",
]
