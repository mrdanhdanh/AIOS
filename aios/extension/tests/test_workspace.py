"""Tests for workspace context adapter."""

from __future__ import annotations

import pytest

from aios.extension.workspace import WorkspaceAdapter


class TestWorkspaceAdapter:
    def test_instantiation(self) -> None:
        adapter = WorkspaceAdapter()
        assert adapter.workspace_root == ""

    def test_set_workspace_root(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_workspace_root("/my/workspace")
        assert adapter.workspace_root == "/my/workspace"

    def test_set_current_file(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_current_file("main.py")
        ctx = adapter.get_context()
        assert ctx.current_file == "main.py"

    def test_set_selection(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_selection("x = 1", "test.py")
        ctx = adapter.get_context()
        assert ctx.selected_code == "x = 1"
        assert ctx.selected_file == "test.py"

    def test_set_selection_uses_current_file(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_current_file("main.py")
        adapter.set_selection("y = 2")
        ctx = adapter.get_context()
        assert ctx.selected_file == "main.py"

    def test_clear_selection(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_selection("x = 1")
        adapter.clear_selection()
        ctx = adapter.get_context()
        assert ctx.selected_code == ""
        assert ctx.selected_file == ""

    def test_set_open_files(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_open_files(["a.py", "b.py"])
        ctx = adapter.get_context()
        assert ctx.open_files == ["a.py", "b.py"]

    def test_set_git_info(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_git_info(branch="main", status="clean", url="https://repo")
        ctx = adapter.get_context()
        assert ctx.git_branch == "main"
        assert ctx.git_status == "clean"
        assert ctx.repository_url == "https://repo"

    def test_to_dict(self) -> None:
        adapter = WorkspaceAdapter(workspace_root="/ws")
        d = adapter.to_dict()
        assert d["workspace_root"] == "/ws"

    def test_context_independent_copy(self) -> None:
        adapter = WorkspaceAdapter()
        adapter.set_open_files(["a.py"])
        ctx1 = adapter.get_context()
        adapter.set_open_files(["b.py"])
        ctx2 = adapter.get_context()
        assert ctx1.open_files == ["a.py"]
        assert ctx2.open_files == ["b.py"]
