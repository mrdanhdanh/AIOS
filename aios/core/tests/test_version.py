"""Tests for :mod:`aios.core.version`."""

from __future__ import annotations

import pytest

from aios.core.version import SemVer, VersionError


class TestSemVerParsing:
    """Verify version string parsing."""

    def test_parse_basic(self):
        v = SemVer.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease == ""
        assert v.build == ""

    def test_parse_prerelease(self):
        v = SemVer.parse("1.0.0-alpha.1")
        assert v.prerelease == "alpha.1"
        assert v.is_prerelease is True

    def test_parse_build_metadata(self):
        v = SemVer.parse("1.0.0+build.123")
        assert v.build == "build.123"

    def test_parse_prerelease_and_build(self):
        v = SemVer.parse("1.0.0-beta.1+sha.abc123")
        assert v.prerelease == "beta.1"
        assert v.build == "sha.abc123"

    def test_parse_zero_version(self):
        v = SemVer.parse("0.0.0")
        assert v.major == 0

    def test_parse_invalid_raises(self):
        with pytest.raises(VersionError, match="Invalid semver"):
            SemVer.parse("not-a-version")

    def test_parse_incomplete_raises(self):
        with pytest.raises(VersionError, match="Invalid semver"):
            SemVer.parse("1.2")

    def test_parse_negative_raises(self):
        with pytest.raises(VersionError):
            SemVer(-1, 0, 0)


class TestSemVerComparison:
    """Verify version comparison operators."""

    def test_equal(self):
        assert SemVer.parse("1.0.0") == SemVer.parse("1.0.0")

    def test_major_less_than(self):
        assert SemVer.parse("1.0.0") < SemVer.parse("2.0.0")

    def test_minor_less_than(self):
        assert SemVer.parse("1.0.0") < SemVer.parse("1.1.0")

    def test_patch_less_than(self):
        assert SemVer.parse("1.0.0") < SemVer.parse("1.0.1")

    def test_prerelease_less_than_release(self):
        assert SemVer.parse("1.0.0-alpha") < SemVer.parse("1.0.0")

    def test_prerelease_comparison(self):
        assert SemVer.parse("1.0.0-alpha") < SemVer.parse("1.0.0-beta")

    def test_prerelease_numeric(self):
        assert SemVer.parse("1.0.0-alpha.1") < SemVer.parse("1.0.0-alpha.2")

    def test_prerelease_fewer_segments(self):
        assert SemVer.parse("1.0.0-alpha") < SemVer.parse("1.0.0-alpha.1")

    def test_build_metadata_ignored(self):
        assert SemVer.parse("1.0.0+a") == SemVer.parse("1.0.0+b")

    def test_greater_than(self):
        assert SemVer.parse("2.0.0") > SemVer.parse("1.0.0")

    def test_hash_consistent(self):
        a = SemVer.parse("1.0.0")
        b = SemVer.parse("1.0.0")
        assert hash(a) == hash(b)
        assert len({a, b}) == 1


class TestSemVerString:
    """Verify string representation."""

    def test_str_basic(self):
        assert str(SemVer.parse("1.2.3")) == "1.2.3"

    def test_str_prerelease(self):
        assert str(SemVer.parse("1.0.0-alpha.1")) == "1.0.0-alpha.1"

    def test_str_build(self):
        assert str(SemVer.parse("1.0.0+build")) == "1.0.0+build"

    def test_repr(self):
        v = SemVer.parse("1.0.0")
        assert "SemVer" in repr(v)
