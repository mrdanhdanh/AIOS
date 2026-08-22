"""Developer Kit (M8 — TASK-047, extended T071 DX)."""
from aios.devkit.contracts import ProjectTemplate, ScaffoldConfig
from aios.devkit.scaffold import (
    DevKitScaffold,
    GeneratedFile,
    KIND_LAYER,
    ScaffoldArtifact,
    VALID_KINDS,
)
from aios.devkit.errors import (
    ActionableError,
    CliStabilityError,
    CliVersionBumpRequired,
    explain,
    format_actionable,
    wrap_error,
)
from aios.devkit.cli_version import CLI_VERSION, CliVersionPolicy
from aios.devkit.cli import DevKitCLI

__all__ = [
    "ProjectTemplate",
    "ScaffoldConfig",
    "DevKitScaffold",
    "GeneratedFile",
    "KIND_LAYER",
    "ScaffoldArtifact",
    "VALID_KINDS",
    "ActionableError",
    "CliStabilityError",
    "CliVersionBumpRequired",
    "explain",
    "format_actionable",
    "wrap_error",
    "CLI_VERSION",
    "CliVersionPolicy",
    "DevKitCLI",
]
