"""
Resilience patterns for robust multi-agent pipelines.

This module provides error handling and recovery mechanisms:
- Retry with exponential backoff (Listing 3.8)
- Checkpointing for resumable runs (Listing 3.9)
- Alert hooks for monitoring (Listing 3.10)
"""

from .retry import retry_stage, RetryConfig
from .checkpoint import Checkpoint, safe_run
from .alerts import AlertHandler, send_alert

__all__ = [
    "retry_stage",
    "RetryConfig",
    "Checkpoint",
    "safe_run",
    "AlertHandler",
    "send_alert",
]
