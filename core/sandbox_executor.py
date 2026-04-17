"""
Sandboxed execution helpers for filesystem and command operations.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict


class SandboxExecutor:
    def __init__(self, root_path: str | None = None):
        self.root = Path(root_path or ".").resolve()
        self.denied_command_tokens = {"rm -rf /", "shutdown", "reboot", ":(){", "mkfs", "dd if="}

    def validate_path(self, path_str: str) -> tuple[bool, str | None]:
        try:
            path = Path(path_str).expanduser().resolve()
            if self.root in path.parents or path == self.root:
                return True, None
            return False, f"Path '{path}' is outside sandbox root '{self.root}'"
        except Exception as exc:
            return False, str(exc)

    def run_command(self, command: str, timeout: int = 30) -> Dict:
        lowered = command.lower()
        for token in self.denied_command_tokens:
            if token in lowered:
                return {"success": False, "error": f"Command blocked by sandbox policy: {token}"}
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.root,
            )
            return {
                "success": completed.returncode == 0,
                "result": {
                    "returncode": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                },
                "error": completed.stderr.strip() if completed.returncode != 0 else None,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
