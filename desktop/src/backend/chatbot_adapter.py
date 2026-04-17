"""
Backend adapter for widget chat requests.
"""
from __future__ import annotations

from typing import Generator

from core.agent_runtime import AgentRuntime
from core.contracts import AgentEvent, EventType, UserRequest
from src.services.api_client import APIClient


class ChatbotAdapter:
    """Cloud-first adapter with runtime contracts and streaming events."""

    def __init__(self):
        self.api_client = APIClient()
        self.runtime = AgentRuntime()

    def get_response(self, message: str) -> str:
        """Compatibility path: gather stream and return final text."""
        final_text = ""
        for event in self.stream_response(message):
            if event.type == EventType.RESPONSE_CHUNK:
                final_text += event.message
            elif event.type == EventType.DONE and event.message:
                final_text = event.message
        return final_text or "No response generated."

    def stream_response(self, message: str, session_id: str = "desktop") -> Generator[AgentEvent, None, None]:
        """Primary runtime stream used by upgraded UI."""
        prompt = message.strip()
        if not prompt:
            yield AgentEvent(type=EventType.ERROR, message="Please enter a message.")
            return

        request = UserRequest(message=prompt, session_id=session_id)
        yield from self.runtime.stream_request(request)

    def resolve_approval(self, approval_id: str, approved: bool):
        """Resolve blocking approval for a pending risky action."""
        self.runtime.resolve_approval(approval_id, approved)

    def _try_api(self, prompt: str) -> str | None:
        """Try local API backend first."""
        response = self.api_client.post("/chat", {"message": prompt})
        if not response:
            return None

        return (
            response.get("response")
            or response.get("message")
            or response.get("answer")
            or (
                response.get("data", {}).get("response")
                if isinstance(response.get("data"), dict)
                else None
            )
        )

    def _try_cloud(self, prompt: str) -> str | None:
        """Fallback to cloud LLM client when available."""
        try:
            from cloud_llm_client import CloudLLMClient

            client = CloudLLMClient()
            if not client.is_available():
                return None
            return client.get_response(prompt, max_length=220, temperature=0.7)
        except Exception:
            return None
