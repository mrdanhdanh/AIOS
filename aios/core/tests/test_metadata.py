"""Tests for :mod:`aios.core.metadata`."""

from __future__ import annotations

import pytest

from aios.core.metadata import BuildInfo, PackageMetadata


class TestPackageMetadata:
    """Verify PackageMetadata.current() returns valid data."""

    def test_current_returns_instance(self):
        meta = PackageMetadata.current()
        assert isinstance(meta, PackageMetadata)

    def test_name_is_aios(self):
        meta = PackageMetadata.current()
        assert meta.name == "aios"

    def test_version_is_nonempty(self):
        meta = PackageMetadata.current()
        assert meta.version  # not empty

    def test_python_version_format(self):
        meta = PackageMetadata.current()
        parts = meta.python_version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_description_is_nonempty(self):
        meta = PackageMetadata.current()
        assert meta.description

    def test_commit_hash_is_string(self):
        meta = PackageMetadata.current()
        assert isinstance(meta.commit_hash, str)

    def test_build_info_populated(self):
        meta = PackageMetadata.current()
        assert isinstance(meta.build_info, BuildInfo)
        assert meta.build_info.commit_hash


class TestAsDict:
    """Verify serialisation."""

    def test_as_dict_has_expected_keys(self):
        meta = PackageMetadata.current()
        d = meta.as_dict()
        assert "name" in d
        assert "version" in d
        assert "python_version" in d
        assert "commit_hash" in d
        assert "build_info" in d
        assert isinstance(d["build_info"], dict)
