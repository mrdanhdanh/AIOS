"""DevKit contracts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ProjectTemplate:
    name: str = ""
    description: str = ""
    files: list = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "files": self.files}

@dataclass
class ScaffoldConfig:
    project_name: str = ""
    template: str = "default"
    author: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"project_name": self.project_name, "template": self.template}
