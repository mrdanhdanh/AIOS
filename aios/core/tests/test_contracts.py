"""Tests for :mod:`aios.core.contracts`."""

from __future__ import annotations

import pytest

from aios.core.contracts import (
    Contract,
    ContractError,
    check_compatibility,
    check_contracts,
)


class TestContractParsing:
    """Verify contract creation and range parsing."""

    def test_create_contract(self):
        c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        assert c.name == "storage"

    def test_invalid_range_raises(self):
        with pytest.raises(ContractError, match="Invalid version range"):
            Contract(name="x", version_range="bad")

    def test_min_ge_max_raises(self):
        with pytest.raises(ContractError, match="must be <"):
            Contract(name="x", version_range=">=2.0.0,<1.0.0")


class TestCompatibility:
    """Verify version compatibility checking."""

    def test_compatible_version(self):
        c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        assert c.is_satisfied_by("1.5.0") is True

    def test_exact_min_version(self):
        c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        assert c.is_satisfied_by("1.0.0") is True

    def test_max_version_excluded(self):
        c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        assert c.is_satisfied_by("2.0.0") is False

    def test_below_min_version(self):
        c = Contract(name="storage", version_range=">=1.0.0,<2.0.0")
        assert c.is_satisfied_by("0.9.0") is False

    def test_prerelease_satisfies(self):
        c = Contract(name="x", version_range=">=1.0.0-beta,<2.0.0")
        assert c.is_satisfied_by("1.0.0-beta.1") is True

    def test_invalid_version_string(self):
        c = Contract(name="x", version_range=">=1.0.0,<2.0.0")
        assert c.is_satisfied_by("not-a-version") is False


class TestCheckCompatibility:
    """Verify the check_compatibility function."""

    def test_passes(self):
        c = Contract(name="x", version_range=">=1.0.0,<2.0.0")
        check_compatibility(c, "1.5.0")  # should not raise

    def test_fails(self):
        c = Contract(name="x", version_range=">=1.0.0,<2.0.0")
        with pytest.raises(ContractError, match="requires"):
            check_compatibility(c, "2.0.0")


class TestCheckContracts:
    """Verify multi-contract checking."""

    def test_all_satisfied(self):
        contracts = [
            Contract(name="a", version_range=">=1.0.0,<2.0.0"),
            Contract(name="b", version_range=">=0.1.0,<1.0.0"),
        ]
        providers = {"a": "1.5.0", "b": "0.5.0"}
        check_contracts(contracts, providers)  # should not raise

    def test_missing_provider(self):
        contracts = [Contract(name="a", version_range=">=1.0.0,<2.0.0")]
        with pytest.raises(ContractError, match="No provider"):
            check_contracts(contracts, {})

    def test_incompatible_provider(self):
        contracts = [Contract(name="a", version_range=">=1.0.0,<2.0.0")]
        with pytest.raises(ContractError, match="requires"):
            check_contracts(contracts, {"a": "2.0.0"})
