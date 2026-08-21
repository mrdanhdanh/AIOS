"""AIOS VS Code Extension — Backend contracts and client layer.

Provides command definitions, workspace context, API client,
and event client for VS Code extension integration.
"""

from aios.extension.api_client import ExtensionApiClient
from aios.extension.config import ExtensionConfig
from aios.extension.contracts import (
    CommandDefinition,
    CommandId,
    DiagnosticSeverity,
    ExtensionDiagnostic,
    WorkspaceContext,
)
from aios.extension.event_client import ExtensionEventClient
from aios.extension.mock_backend import MockExtensionBackend
from aios.extension.workspace import WorkspaceAdapter

__all__ = [
    "CommandDefinition",
    "CommandId",
    "DiagnosticSeverity",
    "ExtensionDiagnostic",
    "WorkspaceContext",
    "ExtensionApiClient",
    "ExtensionEventClient",
    "ExtensionConfig",
    "MockExtensionBackend",
    "WorkspaceAdapter",
]
