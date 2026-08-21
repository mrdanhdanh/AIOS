"""Workspace context adapter for VS Code extension.

Gathers workspace context (files, selections, git state) and packages
them for transmission to the AIOS backend. No policy decisions made locally.

AC-019-03: Workspace context respects Policy.
AC-019-04: No direct Runtime/Tool access.
"""

from __future__ import annotations

from typing import Any

from aios.extension.contracts import WorkspaceContext


class WorkspaceAdapter:
    """Gathers and normalizes workspace context from VS Code.

    All context is sent to the backend for policy evaluation —
    no local policy decisions.
    """

    def __init__(self, workspace_root: str = "") -> None:
        self._workspace_root = workspace_root
        self._current_file: str = ""
        self._selected_code: str = ""
        self._selected_file: str = ""
        self._open_files: list[str] = []
        self._git_branch: str = ""
        self._git_status: str = ""
        self._repository_url: str = ""

    @property
    def workspace_root(self) -> str:
        return self._workspace_root

    def set_workspace_root(self, root: str) -> None:
        self._workspace_root = root

    def set_current_file(self, file_path: str) -> None:
        """Set the currently active file."""
        self._current_file = file_path

    def set_selection(self, code: str, file_path: str = "") -> None:
        """Set the current code selection."""
        self._selected_code = code
        self._selected_file = file_path or self._current_file

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._selected_code = ""
        self._selected_file = ""

    def set_open_files(self, files: list[str]) -> None:
        """Set the list of open files."""
        self._open_files = list(files)

    def set_git_info(self, branch: str = "", status: str = "", url: str = "") -> None:
        """Set git state information."""
        self._git_branch = branch
        self._git_status = status
        self._repository_url = url

    def get_context(self) -> WorkspaceContext:
        """Build a WorkspaceContext from current state.

        AC-019-03: Context is sent to backend for policy evaluation.
        """
        return WorkspaceContext(
            workspace_root=self._workspace_root,
            selected_file=self._selected_file,
            selected_code=self._selected_code,
            current_file=self._current_file,
            open_files=list(self._open_files),
            git_branch=self._git_branch,
            git_status=self._git_status,
            repository_url=self._repository_url,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize current adapter state."""
        return self.get_context().to_dict()
