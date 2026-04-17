"""
Short-term + long-term memory facade for agent runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from memory.memory_manager import MemoryManager


@dataclass
class SessionMemory:
    session_id: str
    recent_messages: List[str] = field(default_factory=list)
    recent_tool_results: List[str] = field(default_factory=list)


class RuntimeMemory:
    """Combines in-memory short context with persistent long memory."""

    def __init__(self):
        self.store = MemoryManager()
        self.sessions: Dict[str, SessionMemory] = {}

    def get_session(self, session_id: str) -> SessionMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id)
        return self.sessions[session_id]

    def remember_turn(self, session_id: str, user_message: str, assistant_message: str):
        session = self.get_session(session_id)
        session.recent_messages.append(f"user: {user_message}")
        session.recent_messages.append(f"assistant: {assistant_message}")
        session.recent_messages = session.recent_messages[-12:]
        self.store.store_conversation(user_message, assistant_message)

    def remember_tool_result(self, session_id: str, result_summary: str):
        session = self.get_session(session_id)
        session.recent_tool_results.append(result_summary)
        session.recent_tool_results = session.recent_tool_results[-10:]

    def build_context(self, session_id: str) -> Dict:
        session = self.get_session(session_id)
        long_term = self.store.get_context(limit=5)
        return {
            "short_term_messages": session.recent_messages,
            "short_term_tool_results": session.recent_tool_results,
            "long_term": long_term,
        }
