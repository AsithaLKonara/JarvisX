"""
Tool schema registry and argument validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


@dataclass
class ToolSchema:
    name: str
    required: List[str] = field(default_factory=list)
    field_types: Dict[str, Type] = field(default_factory=dict)
    risk_level: str = "low"


class ToolSchemaRegistry:
    def __init__(self):
        self.schemas: Dict[str, ToolSchema] = {}
        self._load_defaults()

    def _load_defaults(self):
        self.register(ToolSchema(name="get_current_time", required=[]))
        self.register(ToolSchema(name="list_directory", required=["path"], field_types={"path": str}))
        self.register(ToolSchema(name="read_file", required=["file_path"], field_types={"file_path": str}))
        self.register(ToolSchema(name="write_file", required=["path", "content"], field_types={"path": str, "content": str}, risk_level="medium"))
        self.register(ToolSchema(name="delete_file", required=["path"], field_types={"path": str}, risk_level="high"))
        self.register(ToolSchema(name="launch_app", required=["app"], field_types={"app": str}, risk_level="medium"))
        self.register(ToolSchema(name="execute_command", required=["command"], field_types={"command": str}, risk_level="high"))

    def register(self, schema: ToolSchema):
        self.schemas[schema.name] = schema

    def get(self, name: str) -> Optional[ToolSchema]:
        return self.schemas.get(name)

    def validate(self, name: str, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        schema = self.get(name)
        if not schema:
            return False, f"No schema registered for tool: {name}"
        for required in schema.required:
            if required not in args:
                return False, f"Missing required field '{required}' for tool '{name}'"
        for field, expected_type in schema.field_types.items():
            if field in args and not isinstance(args[field], expected_type):
                return False, f"Field '{field}' for tool '{name}' must be {expected_type.__name__}"
        return True, None
