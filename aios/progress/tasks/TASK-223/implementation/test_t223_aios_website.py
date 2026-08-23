"""AIOS-driven tests for the N5 learning site (TASK-223).

These tests prove the deliverable is produced BY AIOS and behaves correctly:
  1. ``build_n5_site`` (an AIOS tool) generates the site + provenance.
  2. A real Node harness verifies the generated JS logic (quiz scoring,
     vocab filtering, deterministic quiz generation).

This file imports ``aios.*`` so the ``runtime_utilization`` gate detects that
AIOS is genuinely exercised (closing the TASK-222 loophole).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

from aios.tool.website.n5_builder import build_n5_site

IMPL = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(IMPL, "harness_n5.js")


def _have_node() -> bool:
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        return True
    except Exception:
        return False


def test_aios_builds_site_with_evidence():
    tmp = tempfile.mkdtemp()
    try:
        result = build_n5_site(tmp)
        assert os.path.isfile(os.path.join(tmp, "index.html"))
        assert os.path.isfile(os.path.join(tmp, "js", "data.js"))
        assert os.path.isfile(os.path.join(tmp, "js", "app.js"))
        assert os.path.isfile(os.path.join(tmp, "build_evidence.json"))
        ev = json.load(open(os.path.join(tmp, "build_evidence.json"), encoding="utf-8"))
        assert ev["producer"].startswith("aios"), "evidence producer must be an aios.* tool"
        assert ev["content_hash"], "evidence must carry a content_hash"
        assert ev["vocab_count"] >= 100
        assert ev["grammar_count"] >= 10
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_behavior_harness_runs():
    if not _have_node():
        import pytest
        pytest.skip("node not available")
    tmp = tempfile.mkdtemp()
    try:
        build_n5_site(tmp)
        shutil.copy(HARNESS, os.path.join(tmp, "harness_n5.js"))
        r = subprocess.run(
            ["node", "harness_n5.js"], cwd=tmp,
            capture_output=True, text=True,
        )
        assert r.returncode == 0, r.stdout + "\n" + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
