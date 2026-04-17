"""
Runtime contracts for JarvisX agent lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EventType(str, Enum):
    STATE_CHANGED = "state_changed"
    THINKING = "thinking"
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_RESULT = "tool_call_result"
    APPROVAL_REQUIRED = "approval_required"
    RESPONSE_CHUNK = "response_chunk"
    DONE = "done"
    ERROR = "error"


@dataclass
class UserRequest:
    message: str
    user_id: str = "default"
    session_id: str = "desktop"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    risk: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    reason: str = ""


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class AgentPlan:
    intent: str
    reasoning: str
    tool_calls: List[ToolCall] = field(default_factory=list)


@dataclass
class AgentEvent:
    type: EventType
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    text: str
    plan: Optional[AgentPlan] = None
    tool_results: List[ToolResult] = field(default_factory=list)


class AgentState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    RESPONDING = "responding"
    DONE = "done"
    ERROR = "error"
