"""
Core module for Chapter 4: Passive Reconnaissance Agents.

Provides foundational data structures and utilities for artifact management.
"""

from src.core.artifacts import (
    Artifact,
    ScopeArtifact,
    write_jsonl,
    read_jsonl,
    iter_jsonl,
    read_artifacts,
)

__all__ = [
    "Artifact",
    "ScopeArtifact",
    "write_jsonl",
    "read_jsonl",
    "iter_jsonl",
    "read_artifacts",
]
