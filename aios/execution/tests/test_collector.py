"""Tests for the output/artifact collector (T141)."""

import pytest

from aios.execution import CollectedArtifact, OutputArtifactCollector, OutputCapture, redact
from aios.execution._common import ExecutionError


def test_redact_secret():
    assert redact("password=supersecret") == "[REDACTED]"
    assert redact("normal log line") == "normal log line"


def test_capture_empty_fails():
    c = OutputArtifactCollector(policy_ref="pol1")
    with pytest.raises(ExecutionError):
        c.capture_output("run1", "stdout", "")


def test_capture_redacts_and_hashes():
    c = OutputArtifactCollector(policy_ref="pol1")
    cap = c.capture_output("run1", "stdout", "token=abc123")
    assert cap.content == "[REDACTED]"
    assert cap.content_hash


def test_collect_builds_artifact():
    c = OutputArtifactCollector(policy_ref="pol1")
    out = c.capture_output("run1", "stdout", "hello world")
    art = c.collect("run1", [out], artifact_refs=("art1",))
    assert isinstance(art, CollectedArtifact)
    assert art.run_ref == "run1"
    assert art.collector_id
    assert art.artifacts == ["art1"]


def test_collector_id_immutable_required():
    with pytest.raises(ExecutionError):
        CollectedArtifact(run_ref="")


def test_content_hash():
    c = OutputArtifactCollector(policy_ref="pol1")
    out = c.capture_output("run1", "stdout", "hello world")
    art = c.collect("run1", [out])
    assert art.content_hash()


def test_provenance():
    c = OutputArtifactCollector(policy_ref="pol1")
    out = c.capture_output("run1", "stdout", "hello world")
    art = c.collect("run1", [out])
    prov = c.provenance(art)
    assert prov["run_ref"] == "run1"
    assert prov["content_hash"]
