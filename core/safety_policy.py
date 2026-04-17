"""
Safety policy gate for high-risk actions.
"""

from __future__ import annotations

from typing import Dict

from core.contracts import RiskLevel, ToolCall


class SafetyPolicyEngine:
    """Applies risk policies and marks actions requiring approval."""

    HIGH_RISK_KEYWORDS = {
        "delete_file",
        "execute_command",
        "kill_process",
        "shutdown",
        "reboot",
        "rm",
    }
    MEDIUM_RISK_KEYWORDS = {"write_file", "launch_app", "run_workflow"}

    def evaluate(self, call: ToolCall) -> ToolCall:
        normalized = call.name.lower()
        if normalized in self.HIGH_RISK_KEYWORDS:
            call.risk = RiskLevel.HIGH
            call.requires_confirmation = True
            call.reason = "This action can alter system state."
            return call

        if normalized in self.MEDIUM_RISK_KEYWORDS:
            call.risk = RiskLevel.MEDIUM
            call.requires_confirmation = True
            call.reason = "This action may change files or app state."
            return call

        call.risk = RiskLevel.LOW
        call.requires_confirmation = False
        call.reason = "Safe read-only or low-impact action."
        return call

    def approval_payload(self, call: ToolCall) -> Dict[str, str]:
        return {
            "tool_name": call.name,
            "risk": call.risk.value,
            "reason": call.reason,
        }
