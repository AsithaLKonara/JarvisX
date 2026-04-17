"""
Plugin manifest + runtime registry for tool extension.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class PluginToolSpec:
    name: str
    description: str
    permission: str = "standard"


@dataclass
class PluginManifest:
    id: str
    name: str
    version: str
    tools: List[PluginToolSpec] = field(default_factory=list)


class PluginRegistry:
    """Loads plugin manifests and exposes dynamic tool handlers."""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.manifests: Dict[str, PluginManifest] = {}
        self.tool_handlers: Dict[str, Callable[[dict], dict]] = {}
        self._load_manifests()

    def _load_manifests(self):
        if not self.plugins_dir.exists():
            return
        for manifest_file in self.plugins_dir.rglob("plugin.json"):
            try:
                raw = json.loads(manifest_file.read_text(encoding="utf-8"))
                tools = [PluginToolSpec(**tool) for tool in raw.get("tools", [])]
                manifest = PluginManifest(
                    id=raw["id"],
                    name=raw["name"],
                    version=raw.get("version", "1.0.0"),
                    tools=tools,
                )
                self.manifests[manifest.id] = manifest
            except Exception:
                continue

    def register_tool_handler(self, tool_name: str, handler: Callable[[dict], dict]):
        self.tool_handlers[tool_name] = handler

    def get_handler(self, tool_name: str) -> Optional[Callable[[dict], dict]]:
        return self.tool_handlers.get(tool_name)

    def get_tool_catalog(self) -> List[dict]:
        catalog: List[dict] = []
        for manifest in self.manifests.values():
            for tool in manifest.tools:
                catalog.append(
                    {
                        "plugin_id": manifest.id,
                        "plugin_name": manifest.name,
                        "tool_name": tool.name,
                        "description": tool.description,
                        "permission": tool.permission,
                    }
                )
        return catalog
