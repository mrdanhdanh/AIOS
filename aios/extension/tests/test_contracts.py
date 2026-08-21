"""Tests for extension contracts."""

from __future__ import annotations

import pytest

from aios.extension.contracts import (
    COMMAND_API_MAP,
    COMMAND_DEFINITIONS,
    CommandDefinition,
    CommandId,
    CommandRequest,
    CommandResponse,
    DiagnosticSeverity,
    ExtensionDiagnostic,
    WorkspaceContext,
    get_all_commands,
    get_command,
    validate_command_request,
)


class TestCommandId:
    def test_all_commands_exist(self) -> None:
        assert len(CommandId) == 9

    def test_command_values(self) -> None:
        assert CommandId.CHAT.value == "aios.chat"
        assert CommandId.FIX_SELECTION.value == "aios.fixSelection"


class TestCommandApiMap:
    def test_all_commands_mapped(self) -> None:
        for cmd in CommandId:
            assert cmd in COMMAND_API_MAP

    def test_all_endpoints_valid(self) -> None:
        for endpoint in COMMAND_API_MAP.values():
            assert endpoint.startswith("/api/v1/")


class TestCommandDefinition:
    def test_to_dict(self) -> None:
        d = CommandDefinition(
            command_id=CommandId.CHAT,
            title="Chat",
            api_endpoint="/api/v1/orchestrator/decide",
        ).to_dict()
        assert d["command_id"] == "aios.chat"
        assert d["title"] == "Chat"

    def test_requires_defaults(self) -> None:
        cmd = CommandDefinition(
            command_id=CommandId.CHAT,
            title="Chat",
            api_endpoint="/test",
        )
        assert cmd.requires_selection is False
        assert cmd.requires_file is False


class TestWorkspaceContext:
    def test_default(self) -> None:
        ctx = WorkspaceContext()
        assert ctx.has_selection() is False
        assert ctx.has_file() is False

    def test_has_selection(self) -> None:
        ctx = WorkspaceContext(selected_code="  x = 1  ")
        assert ctx.has_selection() is True

    def test_has_file(self) -> None:
        ctx = WorkspaceContext(current_file="test.py")
        assert ctx.has_file() is True

    def test_to_dict(self) -> None:
        ctx = WorkspaceContext(workspace_root="/ws")
        d = ctx.to_dict()
        assert d["workspace_root"] == "/ws"


class TestExtensionDiagnostic:
    def test_to_dict(self) -> None:
        diag = ExtensionDiagnostic(
            severity=DiagnosticSeverity.ERROR,
            message="test error",
        )
        d = diag.to_dict()
        assert d["severity"] == "error"
        assert d["message"] == "test error"


class TestCommandRequest:
    def test_to_dict(self) -> None:
        req = CommandRequest(
            command_id=CommandId.CHAT,
            context=WorkspaceContext(workspace_root="/ws"),
            prompt="hello",
        )
        d = req.to_dict()
        assert d["command_id"] == "aios.chat"
        assert d["prompt"] == "hello"


class TestCommandResponse:
    def test_succeeded(self) -> None:
        resp = CommandResponse(command_id=CommandId.CHAT, status="success")
        assert resp.succeeded is True

    def test_not_succeeded(self) -> None:
        resp = CommandResponse(command_id=CommandId.CHAT, status="error")
        assert resp.succeeded is False

    def test_has_diagnostics(self) -> None:
        resp = CommandResponse(
            command_id=CommandId.CHAT,
            diagnostics=[ExtensionDiagnostic(severity=DiagnosticSeverity.INFO, message="x")],
        )
        assert resp.has_diagnostics is True

    def test_has_artifacts(self) -> None:
        resp = CommandResponse(
            command_id=CommandId.CHAT,
            artifacts=[{"id": "a1"}],
        )
        assert resp.has_artifacts is True


class TestGetAllCommands:
    def test_returns_all(self) -> None:
        cmds = get_all_commands()
        assert len(cmds) == 9

    def test_get_command(self) -> None:
        cmd = get_command(CommandId.CHAT)
        assert cmd is not None
        assert cmd.command_id == CommandId.CHAT

    def test_get_unknown_command(self) -> None:
        assert get_command("bogus") is None


class TestValidateCommandRequest:
    def test_valid_chat(self) -> None:
        req = CommandRequest(
            command_id=CommandId.CHAT,
            context=WorkspaceContext(),
        )
        diagnostics = validate_command_request(req)
        assert len(diagnostics) == 0

    def test_fix_without_selection(self) -> None:
        # FIX_SELECTION requires both selection AND file
        req = CommandRequest(
            command_id=CommandId.FIX_SELECTION,
            context=WorkspaceContext(),
        )
        diagnostics = validate_command_request(req)
        assert len(diagnostics) == 2
        assert all(d.severity == DiagnosticSeverity.WARNING for d in diagnostics)

    def test_explain_without_file(self) -> None:
        req = CommandRequest(
            command_id=CommandId.EXPLAIN,
            context=WorkspaceContext(selected_code="x = 1"),
        )
        diagnostics = validate_command_request(req)
        assert len(diagnostics) == 1

    def test_unknown_command(self) -> None:
        req = CommandRequest(
            command_id="unknown_cmd",  # type: ignore[arg-type]
            context=WorkspaceContext(),
        )
        diagnostics = validate_command_request(req)
        assert len(diagnostics) == 1
        assert diagnostics[0].severity == DiagnosticSeverity.ERROR

