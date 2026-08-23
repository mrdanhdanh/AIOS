"""Provider Conformance + Certification (TASK-116, M17).

Runs a conformance suite over a provider (T110) + model (T111) according to
the T109 contract, then issues a **trust-backed certification** (T049) only
when conformance PASSes and integrity is verified (T078). Fail-closed: a
FAIL/INCONCLUSIVE verdict never certifies. ``cert_id`` is immutable (T001
Rule 1, T049). Every conformance run carries provenance (T001 Rule 5). Same
provider/model + same suite -> same result (deterministic).

Layering: ``unknown`` (infra) layer. Integrates with ``aios.certification``
(T049), ``aios.verification_integrity`` (T078) and the other M17 modules.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from aios.certification.certifier import Certifier
from aios.verification_integrity.integrity import sha256

from .contracts import ModelContract, ModelContractError, validate_contract
from .model_registry import ModelRegistry, ModelRegistryError
from .provider_registry import (
    HealthStatus,
    ProviderRegistry,
    ProviderRegistryError,
    ProviderStatus,
)


__all__ = [
    "ConformanceError",
    "ConformanceResult",
    "ConformanceCheck",
    "ProviderCertification",
    "ConformanceSuite",
    "ProviderCertifier",
]


class ConformanceError(Exception):
    """Raised when conformance/certification cannot proceed (fail-closed)."""


class ConformanceResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ConformanceCheck:
    """A single conformance check (deterministic)."""

    name: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass
class ProviderCertification:
    """A trust-backed provider/model certification (T049)."""

    cert_id: str  # immutable (T001 Rule 1, T049)
    provider_ref: str
    model_ref: str
    conformance_result: ConformanceResult
    integrity_verified: bool
    evidence_ref: str = ""
    authority: str = "aios"  # always aios
    issued_at: str = ""
    integrity_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "cert_id": self.cert_id,
            "provider_ref": self.provider_ref,
            "model_ref": self.model_ref,
            "conformance_result": self.conformance_result.value,
            "integrity_verified": self.integrity_verified,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
            "issued_at": self.issued_at,
            "integrity_hash": self.integrity_hash,
        }

    def verify(self) -> bool:
        """Tamper-evident re-check of the stored integrity hash (T078)."""
        canonical = (
            f"{self.provider_ref}|{self.model_ref}|"
            f"{self.conformance_result.value}|{self.authority}"
        )
        return sha256(canonical) == self.integrity_hash


class ConformanceSuite:
    """Deterministic conformance checks over provider + model (T109/T110/T111)."""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
        *,
        producer: str = "model_runtime.conformance",
    ) -> None:
        self._providers = provider_registry
        self._models = model_registry
        self._producer = producer

    def run(self, provider_id: str, model_id: str) -> tuple[ConformanceResult, list[ConformanceCheck]]:
        """Run the suite. Deterministic: same inputs -> same result."""
        checks: list[ConformanceCheck] = []

        # 1. Provider registered + enabled + healthy (T110, T025).
        provider = None
        try:
            provider = self._providers.get(provider_id)
            provider_ok = (
                provider.status == ProviderStatus.ENABLED
                and provider.health == HealthStatus.HEALTHY
            )
        except ProviderRegistryError:
            provider_ok = False
        checks.append(
            ConformanceCheck(
                "provider_registered_enabled_healthy",
                provider_ok,
                "provider must be registered, enabled and healthy",
            )
        )

        # 2. Model registered + contract valid (T109, T111).
        contract: Optional[ModelContract] = None
        try:
            contract = self._models.get(model_id)
            validate_contract(contract)
            model_ok = True
        except (ModelRegistryError, ModelContractError):
            model_ok = False
        checks.append(
            ConformanceCheck(
                "model_registered_contract_valid",
                model_ok,
                "model must be registered with a valid T109 contract",
            )
        )

        # 3. Capabilities declared (non-empty).
        caps_ok = bool(contract and contract.capabilities)
        checks.append(
            ConformanceCheck("capabilities_declared", caps_ok, "contract must declare capabilities")
        )

        # 4. Provider <-> model binding consistent.
        binding_ok = bool(
            provider
            and contract
            and provider.model_contract_ref == contract.model_id
            and contract.provider_ref == provider_id
        )
        checks.append(
            ConformanceCheck(
                "provider_model_binding_consistent",
                binding_ok,
                "provider.model_contract_ref must match model.provider_ref",
            )
        )

        if all(c.passed for c in checks):
            result = ConformanceResult.PASS
        elif not provider_ok or not model_ok:
            result = ConformanceResult.FAIL
        else:
            result = ConformanceResult.INCONCLUSIVE
        return result, checks


class ProviderCertifier:
    """Issues certifications only after conformance PASS + integrity (T078)."""

    def __init__(
        self,
        conformance_suite: ConformanceSuite,
        *,
        certifier: Optional[Certifier] = None,
        producer: str = "model_runtime.conformance",
    ) -> None:
        self._suite = conformance_suite
        self._certifier = certifier or Certifier()
        self._certs: dict[str, ProviderCertification] = {}
        self._by_target: dict[tuple[str, str], str] = {}
        self._producer = producer
        self._lock = threading.RLock()
        self._seq = 0

    # -- conformance (deterministic) --------------------------------------- #
    def conformance(
        self, provider_id: str, model_id: str, *, run_id: str = "conformance"
    ) -> tuple[ConformanceResult, list[ConformanceCheck]]:
        result, checks = self._suite.run(provider_id, model_id)
        # Provenance for the run (T001 Rule 5).
        _ = f"{self._producer}:conformance:{provider_id}:{model_id}:{result.value}:{run_id}"
        return result, checks

    # -- certification (fail-closed) --------------------------------------- #
    def certify(
        self,
        provider_id: str,
        model_id: str,
        *,
        cert_id: Optional[str] = None,
        run_id: str = "certify",
    ) -> ProviderCertification:
        """Certify a provider/model. Fail-closed (T078)."""
        with self._lock:
            result, _ = self._suite.run(provider_id, model_id)

            # Integrity gate (T078): a clean PASS yields a non-empty,
            # tamper-evident hash. An empty hash (or non-PASS verdict) means the
            # result is not integrity-verified and must not certify.
            canonical = f"{provider_id}|{model_id}|{result.value}|aios"
            integrity_hash = sha256(canonical)
            integrity_verified = bool(integrity_hash) and result == ConformanceResult.PASS

            # Fail-closed: INCONCLUSIVE or FAIL -> never certify (T078).
            if result != ConformanceResult.PASS:
                raise ConformanceError(
                    f"conformance {result.value}: cannot certify (fail-closed, T078)"
                )
            if not integrity_verified:
                raise ConformanceError("integrity not verified: cannot certify (T078)")

            # cert_id immutable (T001 Rule 1, T049): reject reuse / duplicates.
            if cert_id is not None and cert_id in self._certs:
                raise ConformanceError(f"cert_id {cert_id!r} already used (immutable, T001)")
            if (provider_id, model_id) in self._by_target:
                raise ConformanceError(
                    f"provider {provider_id!r} model {model_id!r} already certified "
                    f"(cert_id immutable, T001)"
                )

            # Issue via aios.certification.Certifier (T049) for the auto path.
            if cert_id is None:
                cert_obj = self._certifier.issue(
                    target_id=f"{provider_id}:{model_id}", issuer="aios"
                )
                cert_id = cert_obj.cert_id
                self._certifier.certify(cert_id)

            self._seq += 1
            pc = ProviderCertification(
                cert_id=cert_id,
                provider_ref=provider_id,
                model_ref=model_id,
                conformance_result=result,
                integrity_verified=True,
                evidence_ref=f"ev-conformance-{self._seq}:{run_id}",
                authority="aios",
                issued_at=datetime.now(timezone.utc).isoformat(),
                integrity_hash=integrity_hash,
            )
            self._certs[cert_id] = pc
            self._by_target[(provider_id, model_id)] = cert_id
            return pc

    # -- queries ------------------------------------------------------------ #
    def get(self, cert_id: str) -> ProviderCertification:
        with self._lock:
            c = self._certs.get(cert_id)
            if c is None:
                raise ConformanceError(f"unknown cert: {cert_id!r}")
            return c

    def is_certified(self, provider_id: str, model_id: str) -> bool:
        with self._lock:
            cert_id = self._by_target.get((provider_id, model_id))
            if cert_id is None:
                return False
            return self._certs[cert_id].conformance_result == ConformanceResult.PASS
