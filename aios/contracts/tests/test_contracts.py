"""Conformance and freeze-safety tests for the T064 public contract freeze.

These are the *contract tests* that lock frozen-contract behavior. They are
deterministic and fail-closed: any violation blocks DONE.
"""

from __future__ import annotations

import copy

import pytest

from aios.contracts import (
    ALL_SURFACES,
    Contract,
    ContractFreezeError,
    ContractNotRegisteredError,
    ContractRegistry,
    ContractStatus,
    ContractSurface,
    build_default_registry,
    check_registry_conformance,
    require_conformance,
)


# --------------------------------------------------------------------------- #
# Default 1.0 registry population
# --------------------------------------------------------------------------- #
def test_default_registry_has_five_frozen_surfaces() -> None:
    registry = build_default_registry()
    contracts = registry.frozen_contracts()
    assert len(contracts) == 5
    assert {c.surface for c in contracts} == set(ALL_SURFACES)


def test_default_contracts_are_version_1_0_0_and_frozen() -> None:
    registry = build_default_registry()
    for contract in registry.list_contracts():
        assert contract.version == "1.0.0"
        assert contract.status is ContractStatus.FROZEN


def test_default_registry_conforms() -> None:
    registry = build_default_registry()
    assert check_registry_conformance(registry) == []
    require_conformance(registry)  # must not raise


# --------------------------------------------------------------------------- #
# Lookup / no shadow contract
# --------------------------------------------------------------------------- #
def test_lookup_returns_registered_contract() -> None:
    registry = build_default_registry()
    contract = registry.lookup("aios.api.public")
    assert contract.surface is ContractSurface.API
    assert contract.is_frozen


def test_lookup_unregistered_surface_raises() -> None:
    registry = build_default_registry()
    with pytest.raises(ContractNotRegisteredError):
        registry.lookup("aios.unregistered.surface")


# --------------------------------------------------------------------------- #
# Freeze safety — no silent change
# --------------------------------------------------------------------------- #
def test_silent_change_to_frozen_is_blocked() -> None:
    registry = build_default_registry()
    frozen = registry.lookup("aios.api.public")
    # Same version, different content -> silent change attempt.
    attempt = Contract(
        name=frozen.name,
        version=frozen.version,
        status=ContractStatus.FROZEN,
        surface=frozen.surface,
        compatibility="3.0.0",
        evidence_ref=frozen.evidence_ref,
    )
    with pytest.raises(ContractFreezeError):
        registry.register(attempt, adr_ref="adr:change")


def test_breaking_change_without_adr_is_blocked() -> None:
    registry = build_default_registry()
    frozen = registry.lookup("aios.api.public")
    attempt = Contract(
        name=frozen.name,
        version="2.0.0",  # major bump = breaking change
        status=ContractStatus.FROZEN,
        surface=frozen.surface,
        compatibility="3.0.0",
        evidence_ref=frozen.evidence_ref,
    )
    with pytest.raises(ContractFreezeError):
        registry.register(attempt)  # no adr_ref


def test_breaking_change_with_adr_is_allowed() -> None:
    registry = build_default_registry()
    frozen = registry.lookup("aios.api.public")
    attempt = Contract(
        name=frozen.name,
        version="2.0.0",
        status=ContractStatus.FROZEN,
        surface=frozen.surface,
        compatibility="3.0.0",
        evidence_ref=frozen.evidence_ref,
    )
    result = registry.register(attempt, adr_ref="adr:api-v2-breaking")
    assert result.version == "2.0.0"
    assert registry.adr_ref("aios.api.public") == "adr:api-v2-breaking"
    # Breaking change opens a deprecation window.
    assert registry.deprecation_window("aios.api.public") == "180d"


def test_nonbreaking_change_with_adr_is_allowed() -> None:
    registry = build_default_registry()
    frozen = registry.lookup("aios.schema.public")
    attempt = Contract(
        name=frozen.name,
        version="1.1.0",  # minor bump = additive, backward-compatible
        status=ContractStatus.FROZEN,
        surface=frozen.surface,
        compatibility="2.0.0",
        evidence_ref=frozen.evidence_ref,
    )
    result = registry.register(attempt, adr_ref="adr:schema-v1.1-additive")
    assert result.version == "1.1.0"


def test_draft_contract_may_change_without_adr() -> None:
    registry = ContractRegistry()
    draft = Contract(name="aios.experimental", version="0.1.0", status=ContractStatus.DRAFT)
    registry.register(draft)
    updated = Contract(name="aios.experimental", version="0.2.0", status=ContractStatus.DRAFT)
    # DRAFT contracts are not frozen -> no adr requirement.
    assert registry.register(updated).version == "0.2.0"


# --------------------------------------------------------------------------- #
# Freeze transition
# --------------------------------------------------------------------------- #
def test_freeze_requires_adr() -> None:
    registry = ContractRegistry()
    registry.register(Contract(name="aios.tool.beta", version="0.9.0"))
    with pytest.raises(ContractFreezeError):
        registry.freeze("aios.tool.beta", adr_ref="")


def test_freeze_sets_frozen_status() -> None:
    registry = ContractRegistry()
    registry.register(Contract(name="aios.tool.beta", version="1.0.0"))
    frozen = registry.freeze("aios.tool.beta", adr_ref="adr:tool-freeze")
    assert frozen.status is ContractStatus.FROZEN
    assert registry.adr_ref("aios.tool.beta") == "adr:tool-freeze"


def test_deprecate_marks_deprecated() -> None:
    registry = build_default_registry()
    deprecated = registry.deprecate("aios.event.public", adr_ref="adr:event-deprecate")
    assert deprecated.status is ContractStatus.DEPRECATED


# --------------------------------------------------------------------------- #
# Conformance fail-closed
# --------------------------------------------------------------------------- #
def test_conformance_fails_when_surface_missing() -> None:
    registry = ContractRegistry()
    registry.register(
        Contract(
            name="aios.api.public",
            version="1.0.0",
            status=ContractStatus.FROZEN,
            surface=ContractSurface.API,
            compatibility="2.0.0",
            evidence_ref="adr:x",
        )
    )
    # Only API is covered; SCHEMA/EVENT/CAPABILITY/TOOL are missing.
    violations = check_registry_conformance(registry)
    assert any("SCHEMA" in v for v in violations)
    assert any("EVENT" in v for v in violations)
    assert any("CAPABILITY" in v for v in violations)
    assert any("TOOL" in v for v in violations)
    with pytest.raises(Exception):
        require_conformance(registry)


def test_conformance_fails_when_frozen_missing_evidence() -> None:
    registry = ContractRegistry()
    registry.register(
        Contract(
            name="aios.api.public",
            version="1.0.0",
            status=ContractStatus.FROZEN,
            surface=ContractSurface.API,
            compatibility="",  # missing compatibility
            evidence_ref="",  # missing evidence
        )
    )
    violations = check_registry_conformance(registry)
    assert any("evidence_ref" in v for v in violations)
    assert any("compatibility" in v for v in violations)


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_conformance_is_deterministic() -> None:
    registry = build_default_registry()
    first = check_registry_conformance(registry)
    second = check_registry_conformance(copy.deepcopy(registry))
    assert first == second == []


def test_register_sequence_is_deterministic() -> None:
    def build() -> ContractRegistry:
        r = build_default_registry()
        frozen = r.lookup("aios.api.public")
        r.register(
            Contract(
                name=frozen.name,
                version="2.0.0",
                status=ContractStatus.FROZEN,
                surface=frozen.surface,
                compatibility="3.0.0",
                evidence_ref=frozen.evidence_ref,
            ),
            adr_ref="adr:api-v2-breaking",
        )
        return r

    a = build()
    b = build()
    assert [c.version for c in a.list_contracts()] == [c.version for c in b.list_contracts()]
    assert a.adr_ref("aios.api.public") == b.adr_ref("aios.api.public")
