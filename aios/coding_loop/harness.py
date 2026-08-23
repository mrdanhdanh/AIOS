"""Autonomous Coding Harness (TASK-154, M21).

Integrates the entire coding loop (T145->T153) end-to-end on top of Harness
Kernel T029 + Test Harness T031 + Evaluation Harness T032. TASK-154 is an
*integration harness*, not a new loop. Fail-closed: any break in the loop makes
the run FAIL (never promoted, T078).

Layering: ``coding_loop`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from aios.coding_loop._common import CodingLoopError, _hash, _now
from aios.coding_loop.classification import FailureClassifier
from aios.coding_loop.diagnostic import DiagnosticAgent
from aios.coding_loop.observation import ExecutionObservation
from aios.coding_loop.patch_chain import ContextRefreshPatchChain
from aios.coding_loop.progress_detection import ProgressRegressionDetector
from aios.coding_loop.repair import RepairPlanner
from aios.coding_loop.safety import AutonomousSafetyController
from aios.coding_loop.state_machine import CodingLoopStateMachine
from aios.coding_loop.verification_gate import VerificationGate


class HarnessStatus(str, Enum):
    """Harness run outcome (T154)."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class CodingHarnessRun:
    """Immutable-by-id harness run record (T154)."""

    run_id: str
    loop_ref: str
    safety_ref: Optional[str]
    test_ref: str
    eval_ref: str
    evidence_ref: str
    status: str
    authority: str = "aios"
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.run_id:
            raise CodingLoopError("run_id required (T001 Rule 1, immutable).")
        if not self.evidence_ref:
            raise CodingLoopError("CodingHarnessRun requires evidence_ref (T001 Rule 5).")


class AutonomousCodingHarness:
    """Drives the full coding loop T145->T153 end-to-end, fail-closed (T154)."""

    def __init__(
        self,
        policy_ref: Optional[str] = None,
        guardrail_ref: str = "gr-default",
        baseline: float = 0.0,
    ) -> None:
        self._policy_ref = policy_ref
        self._state_machine = CodingLoopStateMachine(policy_ref=policy_ref)
        self._observation = ExecutionObservation()
        self._classifier = FailureClassifier()
        self._diagnostic = DiagnosticAgent()
        self._repair = RepairPlanner()
        self._detector = ProgressRegressionDetector(baseline=baseline)
        self._gate = VerificationGate()
        self._chain = ContextRefreshPatchChain()
        self._safety = AutonomousSafetyController(guardrail_ref=guardrail_ref)
        self._runs: Dict[str, CodingHarnessRun] = {}

    def run(
        self,
        execution_ref: str,
        trace: tuple,
        progress_metric: float,
        output_hash: str,
        context_ref: str = "ctx-0",
        snapshot: str = "snap-0",
        test_ref: str = "test-0",
        eval_ref: str = "eval-0",
        run_id: Optional[str] = None,
    ) -> CodingHarnessRun:
        sm = self._state_machine
        safety_ref: Optional[str] = None
        status = HarnessStatus.FAIL.value
        # Fail-closed: duplicate run_id is rejected before the loop starts (T001 Rule 1).
        if run_id and run_id in self._runs:
            raise CodingLoopError(f"Duplicate run_id '{run_id}' (T001 Rule 1).")
        try:
            # OBSERVING -> CLASSIFYING
            sm.transition("observe-artifact", policy_ref=self._policy_ref)
            obs = self._observation.capture(
                execution_ref, sm.loop_id, trace, evidence_ref=f"ev-{uuid.uuid4().hex[:12]}"
            )
            # CLASSIFYING -> DIAGNOSING
            sm.transition("classify-artifact", policy_ref=self._policy_ref)
            fc = self._classifier.classify(obs)
            # DIAGNOSING -> REPAIRING
            sm.transition("diagnose-artifact", policy_ref=self._policy_ref)
            rep = self._diagnostic.diagnose(fc, obs)
            if not self._diagnostic.is_promotable(rep):
                raise CodingLoopError("Diagnosis not promotable (T078).")
            # REPAIRING -> VERIFYING
            sm.transition("repair-artifact", policy_ref=self._policy_ref)
            plan = self._repair.plan(rep, rollback_ref=f"rb-{uuid.uuid4().hex[:12]}")
            # VERIFYING -> REFRESHING
            sm.transition("verify-artifact", policy_ref=self._policy_ref)
            prog = self._detector.detect(
                sm.loop_id, plan.plan_id, progress_metric, evidence_ref=f"ev-{uuid.uuid4().hex[:12]}"
            )
            vr = self._gate.verify(prog, output_hash, evidence_ref=f"ev-{uuid.uuid4().hex[:12]}")
            if not self._gate.is_promotable(vr):
                raise CodingLoopError("Verification not promotable (T078).")
            # REFRESHING -> SAFETY
            sm.transition("refresh-artifact", policy_ref=self._policy_ref)
            ctx = self._chain.refresh_context(sm.current_state.value)
            chain = self._chain.refresh_and_chain(
                vr, ctx, snapshot, snapshot, patch_links=[plan.patch_spec]
            )
            dec = self._safety.evaluate(chain, boundary_status="within")
            if dec.kill_switch:
                raise CodingLoopError("Safety kill switch triggered (T068).")
            safety_ref = dec.decision_id
            # SAFETY -> DONE is the final transition of the loop.
            sm.transition("safety-artifact", policy_ref=self._policy_ref)
            status = HarnessStatus.PASS.value
        except CodingLoopError:
            # Fail-closed: any break -> FAIL, never promoted (T078).
            status = HarnessStatus.FAIL.value

        rid = run_id or f"run-{uuid.uuid4().hex[:12]}"
        ev = f"ev-{uuid.uuid4().hex[:12]}"
        run = CodingHarnessRun(
            run_id=rid,
            loop_ref=sm.loop_id,
            safety_ref=safety_ref,
            test_ref=test_ref,
            eval_ref=eval_ref,
            evidence_ref=ev,
            status=status,
        )
        self._runs[rid] = run
        return run

    def get(self, run_id: str) -> CodingHarnessRun:
        if run_id not in self._runs:
            raise CodingLoopError(f"Unknown run '{run_id}'.")
        return self._runs[run_id]

    def provenance(self, run_id: str) -> dict:
        run = self.get(run_id)
        payload = (
            f"{run.run_id}|{run.loop_ref}|{run.safety_ref}|"
            f"{run.test_ref}|{run.eval_ref}|{run.status}|{run.evidence_ref}"
        )
        return {
            "run_id": run.run_id,
            "loop_ref": run.loop_ref,
            "safety_ref": run.safety_ref,
            "test_ref": run.test_ref,
            "eval_ref": run.eval_ref,
            "status": run.status,
            "evidence_ref": run.evidence_ref,
            "authority": run.authority,
            "content_hash": _hash(payload),
        }
