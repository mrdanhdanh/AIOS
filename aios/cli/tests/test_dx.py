"""Tests for the aiagent CLI DX surface (TASK-071)."""
from __future__ import annotations

import json

from aios.cli.workflow_cli import main


def test_version_command(capsys):
    rc = main(["version"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "aios" in out


def test_dx_scaffold_to_disk(capsys, tmp_path):
    out_dir = tmp_path / "gen"
    rc = main(["dx", "scaffold", "capability", "clicap", "--out", str(out_dir)])
    assert rc == 0
    assert (out_dir / "aios" / "capability" / "clicap.py").exists()
    assert (out_dir / "extension_spec.json").exists()


def test_dx_verify_passes(capsys, tmp_path):
    out_dir = tmp_path / "gen"
    assert main(["dx", "scaffold", "tool", "clitool", "--out", str(out_dir)]) == 0
    rc = main(["dx", "verify", str(out_dir)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "[PASS]" in out


def test_dx_policy_stable(capsys):
    rc = main(["dx", "policy", "--baseline", "run,validate", "--current", "run,validate"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "stable" in out


def test_dx_policy_breaking_without_bump(capsys):
    rc = main([
        "dx", "policy",
        "--baseline", "run,validate", "--current", "run",
        "--baseline-version", "1.0.0",
    ])
    # CLI_VERSION is 1.0.0, no bump -> fail-closed.
    assert rc == 1


def test_dx_policy_breaking_with_bump(capsys):
    # Force a bumped current version via monkeypatch of the policy module.
    import aios.devkit.cli_version as cv
    original = cv.CLI_VERSION
    cv.CLI_VERSION = "2.0.0"
    try:
        rc = main([
            "dx", "policy",
            "--baseline", "run,validate", "--current", "run",
            "--baseline-version", "1.0.0",
        ])
    finally:
        cv.CLI_VERSION = original
    out = capsys.readouterr().out
    assert rc == 0
    assert "breaking change detected" in out


def test_scaffold_spec_json_valid(tmp_path):
    out_dir = tmp_path / "gen"
    assert main(["dx", "scaffold", "agent", "cliagent", "--out", str(out_dir)]) == 0
    spec = json.loads((out_dir / "extension_spec.json").read_text(encoding="utf-8"))
    assert spec["name"] == "cliagent"
    assert spec["version"] == "1.0.0"
