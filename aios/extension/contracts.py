"""Extension command definitions and response schemas.

AC-019-01: Commands map to correct AIOS API endpoints.
AC-019-07: Diagnostics show correct severity/state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CommandId(str, Enum):
    """All supported extension commands."""

    CHAT = "aios.chat"
    EXPLAIN = "aios.explain"
    FIX_SELECTION = "aios.fixSelection"
    GENERATE_TEST = "aios.generateTest"
    REVIEW_PR = "aios.reviewPR"
    REFACTOR = "aios.refactor"
    RENAME = "aios.rename"
    ASK_WORKSPACE = "aios.askWorkspace"
    CHAT_WITH_REPO = "aios.chatWithRepository"


# Maps commands to API endpoints
COMMAND_API_MAP: dict[CommandId, str] = {
    CommandId.CHAT: "/api/v1/orchestrator/decide",
    CommandId.EXPLAIN: "/api/v1/orchestrator/decide",
    CommandId.FIX_SELECTION: "/api/v1/orchestrator/decide",
    CommandId.GENERATE_TEST: "/api/v1/orchestrator/decide",
    CommandId.REVIEW_PR: "/api/v1/orchestrator/decide",
    CommandId.REFACTOR: "/api/v1/orchestrator/decide",
    CommandId.RENAME: "/api/v1/orchestrator/decide",
    CommandId.ASK_WORKSPACE: "/api/v1/orchestrator/decide",
    CommandId.CHAT_WITH_REPO: "/api/v1/orchestrator/decide",
}


class DiagnosticSeverity(str, Enum):
    """Diagnostic severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class CommandDefinition:
    """Definition of a single extension command."""

    command_id: CommandId
    title: str
    api_endpoint: str
    requires_selection: bool = False
    requires_file: bool = False
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id.value,
            "title": self.title,
            "api_endpoint": self.api_endpoint,
            "requires_selection": self.requires_selection,
            "requires_file": self.requires_file,
            "description": self.description,
        }


@dataclass
class WorkspaceContext:
    """Context gathered from the VS Code workspace.

    AC-019-03: Workspace context is sent to backend for policy evaluation.
    AC-019-04: No direct Runtime/Tool access from extension.
    """

    workspace_root: str = ""
    selected_file: str = ""
    selected_code: str = ""
    current_file: str = ""
    open_files: list[str] = field(default_factory=list)
    git_branch: str = ""
    git_status: str = ""
    repository_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_root": self.workspace_root,
            "selected_file": self.selected_file,
            "selected_code": self.selected_code,
            "current_file": self.current_file,
            "open_files": self.open_files,
            "git_branch": self.git_branch,
            "git_status": self.git_status,
            "repository_url": self.repository_url,
        }

    def has_selection(self) -> bool:
        """Check if user has selected code."""
        return bool(self.selected_code.strip())

    def has_file(self) -> bool:
        """Check if a file is open/selected."""
        return bool(self.current_file or self.selected_file)


@dataclass
class ExtensionDiagnostic:
    """Diagnostic information for the extension."""

    severity: DiagnosticSeverity
    message: str
    source: str = "aios"
    file: str = ""
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "file": self.file,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class CommandRequest:
    """Request payload for a command execution."""

    command_id: CommandId
    context: WorkspaceContext
    prompt: str = ""
    options: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id.value,
            "context": self.context.to_dict(),
            "prompt": self.prompt,
            "options": self.options,
        }


@dataclass
class CommandResponse:
    """Response from a command execution."""

    command_id: CommandId
    status: str = "success"
    result: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[ExtensionDiagnostic] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id.value,
            "status": self.status,
            "result": self.result,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "artifacts": self.artifacts,
            "error": self.error,
        }

    @property
    def succeeded(self) -> bool:
        return self.status == "success"

    @property
    def has_diagnostics(self) -> bool:
        return len(self.diagnostics) > 0

    @property
    def has_artifacts(self) -> bool:
        return len(self.artifacts) > 0


# Pre-defined command definitions
COMMAND_DEFINITIONS: dict[CommandId, CommandDefinition] = {
    CommandId.CHAT: CommandDefinition(
        command_id=CommandId.CHAT,
        title="AIOS: Chat",
        api_endpoint=COMMAND_API_MAP[CommandId.CHAT],
        description="Chat with AIOS assistant",
    ),
    CommandId.EXPLAIN: CommandDefinition(
        command_id=CommandId.EXPLAIN,
        title="AIOS: Explain",
        api_endpoint=COMMAND_API_MAP[CommandId.EXPLAIN],
        requires_selection=True,
        requires_file=True,
        description="Explain selected code",
    ),
    CommandId.FIX_SELECTION: CommandDefinition(
        command_id=CommandId.FIX_SELECTION,
        title="AIOS: Fix Selection",
        api_endpoint=COMMAND_API_MAP[CommandId.FIX_SELECTION],
        requires_selection=True,
        requires_file=True,
        description="Fix issues in selected code",
    ),
    CommandId.GENERATE_TEST: CommandDefinition(
        command_id=CommandId.GENERATE_TEST,
        title="AIOS: Generate Test",
        api_endpoint=COMMAND_API_MAP[CommandId.GENERATE_TEST],
        requires_file=True,
        description="Generate tests for current file",
    ),
    CommandId.REVIEW_PR: CommandDefinition(
        command_id=CommandId.REVIEW_PR,
        title="AIOS: Review PR",
        api_endpoint=COMMAND_API_MAP[CommandId.REVIEW_PR],
        description="Review pull request",
    ),
    CommandId.REFACTOR: CommandDefinition(
        command_id=CommandId.REFACTOR,
        title="AIOS: Refactor",
        api_endpoint=COMMAND_API_MAP[CommandId.REFACTOR],
        requires_file=True,
        description="Refactor selected code",
    ),
    CommandId.RENAME: CommandDefinition(
        command_id=CommandId.RENAME,
        title="AIOS: Rename",
        api_endpoint=COMMAND_API_MAP[CommandId.RENAME],
        requires_selection=True,
        requires_file=True,
        description="Rename symbol",
    ),
    CommandId.ASK_WORKSPACE: CommandDefinition(
        command_id=CommandId.ASK_WORKSPACE,
        title="AIOS: Ask Workspace",
        api_endpoint=COMMAND_API_MAP[CommandId.ASK_WORKSPACE],
        description="Ask a question about the workspace",
    ),
    CommandId.CHAT_WITH_REPO: CommandDefinition(
        command_id=CommandId.CHAT_WITH_REPO,
        title="AIOS: Chat with Repository",
        api_endpoint=COMMAND_API_MAP[CommandId.CHAT_WITH_REPO],
        description="Chat with context from the entire repository",
    ),
}


def get_all_commands() -> list[CommandDefinition]:
    """Get all registered command definitions."""
    return list(COMMAND_DEFINITIONS.values())


def get_command(command_id: CommandId) -> CommandDefinition | None:
    """Get a command definition by ID."""
    return COMMAND_DEFINITIONS.get(command_id)


def validate_command_request(request: CommandRequest) -> list[ExtensionDiagnostic]:
    """Validate a command request against its definition.

    Returns empty list if valid, diagnostics list if invalid.
    """
    definition = COMMAND_DEFINITIONS.get(request.command_id)
    if definition is None:
        cmd_str = getattr(request.command_id, 'value', str(request.command_id))
        return [
            ExtensionDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                message=f"Unknown command: {cmd_str}",
            )
        ]

    diagnostics: list[ExtensionDiagnostic] = []

    if definition.requires_selection and not request.context.has_selection():
        diagnostics.append(
            ExtensionDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                message=f"Command '{definition.title}' requires code selection",
            )
        )

    if definition.requires_file and not request.context.has_file():
        diagnostics.append(
            ExtensionDiagnostic(
                severity=DiagnosticSeverity.WARNING,
                message=f"Command '{definition.title}' requires an open file",
            )
        )

    return diagnostics
