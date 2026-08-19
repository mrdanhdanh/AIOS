"""Tests for the TASK-002 implementation artifact (no os/pathlib import)."""
import sys

# Make this folder importable without os/pathlib (string-only path resolution).
_dir = str(__file__).replace("\\", "/").rsplit("/", 1)[0]
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from aios_core import (  # noqa: E402
    CORE_METADATA,
    RuntimeConfig,
    configure_logging,
    healthcheck,
    __version__,
    __milestone__,
)


def test_artifact_reexports_match_core():
    assert __version__ == "0.1.0"
    assert __milestone__ == "M1"
    assert CORE_METADATA["name"] == "aios_core"


def test_artifact_healthcheck():
    assert healthcheck()["status"] == "healthy"


def test_artifact_config_defaults():
    cfg = RuntimeConfig()
    assert cfg.offline_first is True
    assert "metadata" in cfg.as_dict()
    assert cfg.as_dict()["metadata"]["version"] == __version__
