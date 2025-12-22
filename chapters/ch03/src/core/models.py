"""
Core data models for AI agent architecture.

Duplicated from Chapter 2 for self-contained usage.

This module defines the fundamental data structures used throughout the agent framework:
- Message: Represents communication between components (user, agent, system, tool)
- Observation: Captures tool execution results and metadata
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class Message(BaseModel):
    """
    Represents a message in the agent conversation.

    Messages are the primary communication medium between different components:
    - system: Configuration and context
    - user: Human input or requests
    - agent: AI-generated responses and reasoning
    - tool: Tool execution requests

    Attributes:
        role: The sender type (system, user, agent, tool)
        content: Natural language text content
        timestamp: When the message was created (UTC)
        meta: Optional metadata dictionary for additional context
    """

    role: str  # "system", "user", "agent", "tool"
    content: str  # natural-language text
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[Dict[str, Any]] = None


class Observation(BaseModel):
    """
    Captures the result of a tool execution.

    Observations provide structured feedback about tool invocations,
    enabling the agent to learn from successes and failures.

    Attributes:
        tool_name: Name of the tool that was executed
        input: Parameters passed to the tool
        output: Structured result from the tool
        success: Whether the execution completed successfully
        error: Error message if execution failed (None if successful)
        timestamp: When the observation was recorded (UTC)
    """

    tool_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
