from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class Message(BaseModel):
    role: str                # "system", "user", "agent", "tool"
    content: str             # natural-language text
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[Dict[str, Any]] = None

class Observation(BaseModel):
    tool_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
