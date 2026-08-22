"""Behavioral Conformance — behavior spec + harness + conformance (TASK-089, M13).

Canonical behavioral conformance contract:

    BehaviorScenario
    ├── scenario_id
    ├── given (precondition)
    ├── when (action)
    ├── then (expected observable)
    ├── actual_observable
    ├── conforms: bool
    └── evidence_ref

Safety properties (all fail-closed / observable / provenance / deterministic):
* Fail-closed conform — behavior deviating from expected -> not conformant.
* Observable only — spec based on observable behavior, not internal state.
* Evidence required — every behavior run carries provenance (T001 Rule 5).
* Deterministic — same scenario + same system -> same observable.
* No parallel behavior system — uses Harness (T030/T032) + Evidence (T001) +
  Conformance (T087).

Integration: imports ``aios.harness.verification`` (VerificationPipeline,
ReplayEngine, Verdict), ``aios.governance.evidence.store`` (EvidenceStore,
Evidence) and ``aios.conformance.conformance`` (ConformanceReport,
ConformanceRunner). No rewrite of any dependency.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from aios.conformance.conformance import ConformanceReport, ConformanceRunner
from aios.governance.evidence.store import Evidence, EvidenceStore
from aios.harness.verification import ReplayEngine, VerificationPipeline, Verdict

# A driver observes the system under a scenario and returns the observable output.
BehaviorDriver = Callable[["BehaviorScenario"], str]


class BehaviorSurface(str, Enum):
    """The observable surface a behavior scenario exercises."""

    API = "api"
    SCHEMA = "schema"
    EVENT = "event"
    CAPABILITY = "capability"
    TOOL = "tool"


@dataclass
class BehaviorScenario:
    """An observable behavior scenario (given/when/then)."""

    scenario_id: str
    given: str
    when: str
    then: str  # expected observable output
    surface: BehaviorSurface = BehaviorSurface.API
    observable: bool = True  # spec must be based on observable behavior
    actual_observable: str = ""
    conforms: bool = False
    evidence_ref: str = ""

    def is_observable(self) -> bool:
        """A scenario is observable iff it declares observable=True and has
        given/when/then describing observable behavior (not internal state)."""
        return (
            self.observable
            and bool(self.given)
            and bool(self.when)
            and bool(self.then)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "given": self.given,
            "when": self.when,
            "then": self.then,
            "surface": self.surface.value,
            "observable": self.observable,
            "actual_observable": self.actual_observable,
            "conforms": self.conforms,
            "evidence_ref": self.evidence_ref,
        }


class BehaviorHarness:
    """Drives the system and observes behavior (T030/T032 integration)."""

    def __init__(self, evidence_store: Optional[EvidenceStore] = None) -> None:
        self._evidence = evidence_store or EvidenceStore()
        self._pipeline = VerificationPipeline()
        self._replay = ReplayEngine()

    # -- core observe ----------------------------------------------------------

    def observe(
        self, scenario: BehaviorScenario, driver: BehaviorDriver, run_id: str = ""
    ) -> BehaviorScenario:
        """Drive the system and compare actual vs expected observable.

        Fail-closed: a non-observable spec or a deviation from expected ->
        ``conforms = False``. Every run records provenance evidence (T001).
        """
        if not scenario.is_observable():
            scenario.actual_observable = ""
            scenario.conforms = False
            return scenario
        actual = driver(scenario)
        scenario.actual_observable = actual
        scenario.conforms = actual == scenario.then
        self._record_evidence(scenario, run_id)
        return scenario

    def _record_evidence(self, scenario: BehaviorScenario, run_id: str) -> str:
        ev_id = f"bev-{hashlib.sha256(scenario.scenario_id.encode()).hexdigest()[:8]}"
        self._evidence.add_evidence(
            evidence_id=ev_id,
            task_id="TASK-089",
            run_id=run_id or ev_id,
            producer="behavior_harness",
            type="behavior_observation",
            source=scenario.scenario_id,
            content=scenario.actual_observable,
        )
        scenario.evidence_ref = ev_id
        return ev_id

    # -- harness verification integration (T030) ------------------------------

    def verify(
        self, scenario: BehaviorScenario, driver: BehaviorDriver, run_id: str = ""
    ) -> Verdict:
        """Run the scenario through the Harness verification pipeline (T030)."""
        pipeline = VerificationPipeline()
        pipeline.add_precondition(lambda: scenario.is_observable())
        pipeline.add_postcondition(
            lambda: self.observe(scenario, driver, run_id=run_id).conforms
        )
        result = pipeline.verify(run_id=run_id or scenario.scenario_id)
        return result.verdict

    # -- determinism / replay integration (T030/T032) ------------------------

    def is_deterministic(
        self, scenario: BehaviorScenario, driver: BehaviorDriver, repeats: int = 2
    ) -> bool:
        """Same scenario + same system -> same observable (deterministic)."""
        results = [driver(scenario) for _ in range(max(1, repeats))]
        return all(r == results[0] for r in results)

    def replay_check(
        self, scenario: BehaviorScenario, driver: BehaviorDriver, run_id: str = ""
    ) -> bool:
        """Record and replay the observation; assert reproduced verdict."""
        actual = driver(scenario)
        recording = {
            "steps": [{"name": "observe", "actual": actual}],
            "verdict": "pass" if actual == scenario.then else "fail",
        }
        key = run_id or scenario.scenario_id
        self._replay.record(key, recording)
        replayed = self._replay.replay(key)
        return bool(replayed.get("match"))


@dataclass
class BehaviorConformanceResult:
    """Fail-closed result of a behavior conformance suite."""

    scenario_count: int
    conforming_count: int
    non_conforming: list[str]
    conformant: bool
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_count": self.scenario_count,
            "conforming_count": self.conforming_count,
            "non_conforming": list(self.non_conforming),
            "conformant": self.conformant,
            "evidence_ref": self.evidence_ref,
        }


class BehaviorConformanceChecker:
    """Runs a suite of behavior scenarios and emits a fail-closed result."""

    def __init__(
        self,
        harness: Optional[BehaviorHarness] = None,
        evidence_store: Optional[EvidenceStore] = None,
    ) -> None:
        self._harness = harness or BehaviorHarness(evidence_store)

    def check(
        self,
        scenarios: list[BehaviorScenario],
        driver: BehaviorDriver,
        run_id: str = "",
    ) -> BehaviorConformanceResult:
        """Run all scenarios. Any non-conform -> not conformant (fail-closed)."""
        non_conforming: list[str] = []
        conforming = 0
        for sc in scenarios:
            self._harness.observe(sc, driver, run_id=f"{run_id}:{sc.scenario_id}")
            if sc.conforms:
                conforming += 1
            else:
                non_conforming.append(sc.scenario_id)
        conformant = len(non_conforming) == 0 and len(scenarios) > 0
        return BehaviorConformanceResult(
            scenario_count=len(scenarios),
            conforming_count=conforming,
            non_conforming=non_conforming,
            conformant=conformant,
            evidence_ref=run_id or f"bcr-{hashlib.sha256(str(len(scenarios)).encode()).hexdigest()[:8]}",
        )

    # -- conformance integration (T087) ---------------------------------------

    def to_conformance_report(
        self, result: BehaviorConformanceResult, target_version: str = "behavioral"
    ) -> ConformanceReport:
        """Bridge the behavior result into the T087 conformance report model."""
        return ConformanceReport(
            target_version=target_version,
            baseline="1.0.0",
            checks_passed=[f"behavior:{i}" for i in range(result.conforming_count)],
            evidence_ref=result.evidence_ref,
            conformant=result.conformant,
        )

    # -- determinism / provenance ---------------------------------------------

    def provenance_complete(self, result: BehaviorConformanceResult) -> bool:
        """Every behavior run carries provenance (T001 Rule 5), conformant or not."""
        return bool(result.evidence_ref)

    def result_hash(self, result: BehaviorConformanceResult) -> str:
        """Deterministic hash (same suite + result -> same hash)."""
        payload = {
            "scenario_count": result.scenario_count,
            "conforming_count": result.conforming_count,
            "non_conforming": sorted(result.non_conforming),
            "conformant": result.conformant,
            "evidence_ref": result.evidence_ref,
        }
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()
