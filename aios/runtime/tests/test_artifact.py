"""Automated tests for the runtime artifact store (TASK-004)."""

import pytest

from aios.runtime.artifact import Artifact, ArtifactError, ArtifactStore


def test_artifact_create_computes_checksum():
    art = Artifact.create("spec.yaml", "name: demo", content_type="text/yaml")
    assert art.checksum == __import__("hashlib").sha256(b"name: demo").hexdigest()
    assert art.verify()


def test_artifact_accepts_bytes():
    art = Artifact.create("bin", b"\x00\x01\x02")
    assert isinstance(art.content, bytes)
    assert art.verify()


def test_artifact_invalid_version_rejected():
    with pytest.raises(ArtifactError):
        Artifact.create("x", "data", version="not-a-version")


def test_artifact_non_str_bytes_rejected():
    with pytest.raises(ArtifactError):
        Artifact.create("x", 12345)


def test_store_put_and_get():
    store = ArtifactStore()
    art = Artifact.create("cfg", "k=v")
    store.put(art)
    assert store.get(art.artifact_id).name == "cfg"
    assert len(store) == 1


def test_store_rejects_bad_checksum():
    store = ArtifactStore()
    art = Artifact.create("cfg", "k=v")
    art.content = b"tampered"
    with pytest.raises(ArtifactError):
        store.put(art)


def test_store_rejects_duplicate_id():
    store = ArtifactStore()
    store.put(Artifact.create("cfg", "v1", version="1.0.0"))
    dup = Artifact.create("cfg", "v2", version="1.0.1", artifact_id=store._store and None)
    # Build a second artifact with the same id as the first.
    first_id = next(iter(store._store))
    dup2 = Artifact.create("cfg", "v3", version="1.0.2", artifact_id=first_id)
    with pytest.raises(ArtifactError):
        store.put(dup2)


def test_store_versions_sorted_by_semver():
    store = ArtifactStore()
    store.put(Artifact.create("lib", "a", version="1.0.0"))
    store.put(Artifact.create("lib", "b", version="1.2.0"))
    store.put(Artifact.create("lib", "c", version="0.9.0"))
    versions = [a.version for a in store.versions("lib")]
    assert versions == ["0.9.0", "1.0.0", "1.2.0"]


def test_store_get_latest():
    store = ArtifactStore()
    store.put(Artifact.create("lib", "a", version="1.0.0"))
    store.put(Artifact.create("lib", "b", version="2.3.1"))
    latest = store.get_latest("lib")
    assert latest is not None and latest.version == "2.3.1"


def test_store_verify_all():
    store = ArtifactStore()
    store.put(Artifact.create("a", "x"))
    store.put(Artifact.create("b", "y"))
    assert store.verify_all()


def test_store_delete():
    store = ArtifactStore()
    art = Artifact.create("a", "x")
    store.put(art)
    store.delete(art.artifact_id)
    assert not store.exists(art.artifact_id)
