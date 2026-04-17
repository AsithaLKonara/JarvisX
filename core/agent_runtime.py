"""
Cloud-first agent runtime with structured tool-calling and event streaming.
"""

from __future__ import annotations

import json
import re
import threading
import uuid
from typing import Callable, Dict, Generator, List, Optional

from cloud_llm_client import CloudLLMClient
from core.contracts import (
    AgentEvent,
    AgentState,
    AgentPlan,
    AgentResponse,
    EventType,
    ToolCall,
    ToolResult,
    UserRequest,
)
from core.plugin_runtime import PluginRegistry
from core.safety_policy import SafetyPolicyEngine
from core.tool_schema import ToolSchemaRegistry
from core.tool_router import ToolRouter
from memory.runtime_memory import RuntimeMemory


class AgentRuntime:
    """Primary runtime used by desktop adapter."""

    def __init__(self, approval_handler: Optional[Callable[[str, ToolCall], bool]] = None):
        self.cloud = CloudLLMClient()
        self.tool_router = ToolRouter()
        self.policy = SafetyPolicyEngine()
        self.plugins = PluginRegistry()
        self.schemas = ToolSchemaRegistry()
        self.memory = RuntimeMemory()
        self.state = AgentState.IDLE
        self.approval_handler = approval_handler
        self._approval_decisions: Dict[str, bool] = {}
        self._approval_events: Dict[str, threading.Event] = {}
        self._register_builtin_plugin_handlers()

    def _register_builtin_plugin_handlers(self):
        # Example plugin execution handler for extension packs.
        self.plugins.register_tool_handler(
            "plugin.echo",
            lambda args: {"success": True, "result": {"echo": args.get("text", "")}},
        )

    def stream_request(self, request: UserRequest) -> Generator[AgentEvent, None, AgentResponse]:
        yield from self._set_state(AgentState.PLANNING)
        context = self.memory.build_context(request.session_id)
        yield AgentEvent(type=EventType.THINKING, message="Analyzing intent...", payload={"context": context})

        plan = self._build_plan(request, context)
        final_text_parts: List[str] = []
        tool_results: List[ToolResult] = []

        for call in plan.tool_calls:
            ok, err = self.schemas.validate(call.name, call.arguments)
            if not ok:
                tool_results.append(ToolResult(tool_name=call.name, success=False, error=err))
                yield AgentEvent(type=EventType.ERROR, message=err or "Schema validation failed")
                continue
            call = self.policy.evaluate(call)
            if call.requires_confirmation:
                approval_id = f"approval-{uuid.uuid4().hex[:10]}"
                yield from self._set_state(AgentState.WAITING_APPROVAL)
                yield AgentEvent(
                    type=EventType.APPROVAL_REQUIRED,
                    message=f"Approval required: {call.name}",
                    payload={**self.policy.approval_payload(call), "approval_id": approval_id},
                )
                approved = self._await_approval(approval_id, call)
                if not approved:
                    tool_results.append(
                        ToolResult(
                            tool_name=call.name,
                            success=False,
                            error="User denied action",
                        )
                    )
                    yield AgentEvent(
                        type=EventType.TOOL_CALL_RESULT,
                        message=f"{call.name} denied by user",
                        payload={"tool": call.name, "error": "denied"},
                    )
                    continue

            yield from self._set_state(AgentState.EXECUTING)
            yield AgentEvent(
                type=EventType.TOOL_CALL_STARTED,
                message=f"Executing {call.name}",
                payload={"tool": call.name, "args": call.arguments},
            )

            result = self._execute_tool(call)
            tool_results.append(result)
            self.memory.remember_tool_result(request.session_id, f"{call.name}: {'ok' if result.success else 'fail'}")
            yield AgentEvent(
                type=EventType.TOOL_CALL_RESULT,
                message=f"{call.name} {'completed' if result.success else 'failed'}",
                payload={"tool": call.name, "result": result.result, "error": result.error},
            )

        yield from self._set_state(AgentState.RESPONDING)
        response_text = self._synthesize_response(request, plan, tool_results)
        for token in self._token_stream(response_text):
            final_text_parts.append(token)
            yield AgentEvent(type=EventType.RESPONSE_CHUNK, message=token)

        final_text = "".join(final_text_parts).strip()
        self.memory.remember_turn(request.session_id, request.message, final_text)
        yield from self._set_state(AgentState.DONE)
        yield AgentEvent(type=EventType.DONE, message=final_text)
        yield from self._set_state(AgentState.IDLE)
        return AgentResponse(text=final_text, plan=plan, tool_results=tool_results)

    def resolve_approval(self, approval_id: str, approved: bool):
        self._approval_decisions[approval_id] = approved
        evt = self._approval_events.get(approval_id)
        if evt:
            evt.set()

    def _build_plan(self, request: UserRequest, context: dict) -> AgentPlan:
        cloud_reasoning = self._cloud_plan_text(request.message, context)
        tool_calls = self._extract_tool_calls(request.message)
        return AgentPlan(intent="desktop_automation", reasoning=cloud_reasoning, tool_calls=tool_calls)

    def _cloud_plan_text(self, message: str, context: dict) -> str:
        if self.cloud.is_available():
            try:
                prompt = (
                    "You are JarvisX planner. Return concise execution reasoning only.\n"
                    f"User message: {message}\n"
                    f"Context: {json.dumps(context)[:1200]}"
                )
                return self.cloud.get_response(prompt, max_length=180, temperature=0.2)
            except Exception:
                pass
        return "Cloud unavailable; using local heuristic planner."

    def _extract_tool_calls(self, text: str) -> List[ToolCall]:
        lowered = text.lower()
        calls: List[ToolCall] = []
        folder_match = re.search(r"(?:folder|directory)\s+(?:named\s+)?([A-Za-z0-9_\-]+)", lowered)
        if "create" in lowered and folder_match:
            folder_name = folder_match.group(1)
            calls.append(ToolCall(name="write_file", arguments={"path": f"{folder_name}/.keep", "content": ""}))
        if "open" in lowered and ("vscode" in lowered or "cursor" in lowered):
            app_name = "cursor" if "cursor" in lowered else "vscode"
            calls.append(ToolCall(name="launch_app", arguments={"app": app_name}))
        if "list" in lowered and "files" in lowered:
            calls.append(ToolCall(name="list_directory", arguments={"path": "."}))
        if "delete" in lowered:
            calls.append(ToolCall(name="delete_file", arguments={"path": "target_path"}))
        if "run" in lowered and "command" in lowered:
            calls.append(ToolCall(name="execute_command", arguments={"command": "echo placeholder"}))
        if not calls:
            calls.append(ToolCall(name="get_current_time", arguments={}))
        return calls

    def _execute_tool(self, call: ToolCall) -> ToolResult:
        plugin_handler = self.plugins.get_handler(call.name)
        if plugin_handler:
            try:
                result = plugin_handler(call.arguments)
                return ToolResult(tool_name=call.name, success=result.get("success", False), result=result.get("result", {}))
            except Exception as exc:
                return ToolResult(tool_name=call.name, success=False, error=str(exc))

        routed = self.tool_router.route_structured_call(call.name, call.arguments)
        return ToolResult(
            tool_name=call.name,
            success=routed.get("success", False),
            result=routed.get("result", {}),
            error=routed.get("error"),
        )

    def _await_approval(self, approval_id: str, call: ToolCall) -> bool:
        if self.approval_handler:
            return self.approval_handler(approval_id, call)
        evt = threading.Event()
        self._approval_events[approval_id] = evt
        # Wait up to 120s for UI decision.
        evt.wait(timeout=120)
        decision = self._approval_decisions.pop(approval_id, False)
        self._approval_events.pop(approval_id, None)
        return decision

    def _set_state(self, state: AgentState) -> Generator[AgentEvent, None, None]:
        self.state = state
        yield AgentEvent(type=EventType.STATE_CHANGED, message=state.value, payload={"state": state.value})

    def _synthesize_response(self, request: UserRequest, plan: AgentPlan, results: List[ToolResult]) -> str:
        summary = ", ".join(
            [f"{r.tool_name}:{'ok' if r.success else 'failed'}" for r in results]
        )
        if self.cloud.is_available():
            try:
                prompt = (
                    "You are JarvisX assistant. Create a concise actionable response.\n"
                    f"User: {request.message}\n"
                    f"Plan reasoning: {plan.reasoning}\n"
                    f"Tool results: {summary}"
                )
                return self.cloud.get_response(prompt, max_length=220, temperature=0.4)
            except Exception:
                pass
        return f"Execution complete. Plan: {plan.reasoning} Results: {summary}."

    @staticmethod
    def _token_stream(text: str) -> Generator[str, None, None]:
        for part in text.split():
            yield part + " "
