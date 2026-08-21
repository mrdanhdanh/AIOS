"""DevKitScaffold."""
from __future__ import annotations
from aios.devkit.contracts import ProjectTemplate, ScaffoldConfig

class DevKitScaffold:
    def __init__(self) -> None:
        self._templates: dict[str, ProjectTemplate] = {}
    def register_template(self, template: ProjectTemplate) -> None:
        self._templates[template.name] = template
    def get_template(self, name: str) -> ProjectTemplate | None: return self._templates.get(name)
    def scaffold(self, config: ScaffoldConfig) -> dict:
        template = self._templates.get(config.template, ProjectTemplate(name=config.template))
        return {"project": config.project_name, "template": template.name, "files": template.files, "status": "created"}
    def list_templates(self) -> list[ProjectTemplate]: return list(self._templates.values())
