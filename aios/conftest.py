"""Shared pytest fixtures for the AIOS test suite.

Fixtures:
    project_root — absolute path to the AIOS workspace root.
    tmp_config   — a Config backed by a temporary directory.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def project_root() -> Path:
    """Return the absolute path to the AIOS workspace root."""
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture()
def tmp_config(tmp_path: Path):
    """Return a Config that uses a temporary directory for config_dir."""
    from aios.core.config import Config

    return Config(
        config_dir=str(tmp_path / ".aios"),
    )
