"""Experiment Controller (TASK-058).

Propose → Authorize → Run (Harness) → Evaluate → Promotion Decision. The
controller never deploys a production change and never calls production
capabilities directly; it only produces a `PromotionDecision` artifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.autonomous_experimentation.contracts import (
    Experiment,
    ExperimentStatus,
    MetricSpec,
    PromotionDecision,
)

_VAGUE_TERMS = ("better", "improve", "good", "faster", "nicer")
_MUTABLE_VERSION_TOKENS = ("latest", "current", "head", "master", "main", "")


class ExperimentController:
    def __init__(
        self,
        governor_allow: Callable[[Experiment], bool] | None = None,
        harness_run: Callable[[Experiment], dict[str, Any]] | None = None,
    ) -> None:
        self._governor = governor_allow
        self._harness_run = harness_run  # runs candidate under Harness only

    # ---- propose --------------------------------------------------------
    def propose(
        self,
        hypothesis: str,
        baseline_ref: str,
        baseline_version: str,
        candidate_ref: str,
        candidate_version: str,
        scenario_ref: str,
        metric_spec: list[MetricSpec],
        policy_scope: str = "",
        evidence_ref: str = "",
    ) -> tuple[Experiment | None, str]:
        # Validate metric_spec is concrete (not LLM-defined vague).
        if not metric_spec:
            return None, "metric_spec is empty (no measurable criteria)"
        for m in metric_spec:
            if not m.name or m.threshold == 0.0 and m.direction == "increase":
                # a zero-threshold increase is effectively vague
                if m.threshold == 0.0:
                    return None, f"metric {m.name!r} has no meaningful threshold"
        # Baseline/candidate/scenario must be immutable/versioned.
        for label, ref, ver in (
            ("baseline", baseline_ref, baseline_version),
            ("candidate", candidate_ref, candidate_version),
            ("scenario", scenario_ref, "x"),  # scenario must be present
        ):
            if not ref:
                return None, f"{label}_ref is required"
            if label != "scenario" and str(ver).lower() in _MUTABLE_VERSION_TOKENS:
                return None, f"{label}_version must be immutable, got {ver!r}"
        if not scenario_ref:
            return None, "scenario_ref is required (experiment must run in Harness)"
        exp = Experiment(
            hypothesis=hypothesis,
            baseline_ref=baseline_ref,
            baseline_version=baseline_version,
            candidate_ref=candidate_ref,
            candidate_version=candidate_version,
            scenario_ref=scenario_ref,
            metric_spec=list(metric_spec),
            policy_scope=policy_scope,
            evidence_ref=evidence_ref,
            status=ExperimentStatus.PROPOSED,
        )
        return exp, ""

    # ---- authorize ------------------------------------------------------
    def authorize(self, exp: Experiment) -> ExperimentStatus:
        if self._governor is not None and not self._governor(exp):
            exp.status = ExperimentStatus.REJECTED
            return exp.status
        exp.status = ExperimentStatus.AUTHORIZED
        return exp.status

    # ---- run (harness only) --------------------------------------------
    def run(self, exp: Experiment) -> dict[str, Any]:
        if exp.status not in (ExperimentStatus.AUTHORIZED, ExperimentStatus.PROPOSED):
            return {"verdict": "blocked", "reason": "not authorized"}
        exp.status = ExperimentStatus.RUNNING
        if self._harness_run is None:
            return {"verdict": "inconclusive", "reason": "no harness runner"}
        result = self._harness_run(exp)
        exp.status = ExperimentStatus.EVALUATED
        return result

    # ---- evaluate / promotion gate -------------------------------------
    def evaluate(
        self,
        exp: Experiment,
        baseline_result: dict[str, Any],
        candidate_result: dict[str, Any],
        policy_pass: bool,
    ) -> PromotionDecision:
        verdict = str(candidate_result.get("verdict", "unknown")).lower()
        # INCONCLUSIVE / UNKNOWN never promote (fail-closed).
        if verdict in ("inconclusive", "unknown", "fail"):
            exp.status = ExperimentStatus.REJECTED
            return PromotionDecision("NOT_PROMOTED", f"verdict {verdict} cannot promote", exp.experiment_id)

        # 1. Verified improvement on quality metrics.
        improved = True
        metrics: dict[str, Any] = {}
        for m in exp.metric_spec:
            base = baseline_result.get(m.name)
            cand = candidate_result.get(m.name)
            if base is None or cand is None:
                improved = False
                metrics[m.name] = {"base": base, "cand": cand, "ok": False}
                continue
            if m.direction == "increase":
                ok = float(cand) >= float(base) + m.threshold
            elif m.direction == "decrease":
                ok = float(cand) <= float(base) - m.threshold
            else:
                ok = abs(float(cand) - float(base)) <= m.threshold
            metrics[m.name] = {"base": base, "cand": cand, "ok": ok}
            if not ok:
                improved = False

        # 2. No prohibited regression (cost/latency/failure).
        regression = False
        for key in ("cost", "latency", "failure"):
            base = baseline_result.get(key)
            cand = candidate_result.get(key)
            if base is not None and cand is not None and float(cand) > float(base) * 1.5:
                regression = True
                metrics[f"{key}_regression"] = True

        # 3. Policy PASS.
        if improved and not regression and policy_pass:
            exp.status = ExperimentStatus.PROMOTION_READY
            return PromotionDecision("PROMOTION_READY", "verified improvement, no regression, policy pass",
                                     exp.experiment_id, metrics)
        exp.status = ExperimentStatus.REJECTED
        reason = "quality regression" if not improved else ("prohibited regression" if regression else "policy fail")
        return PromotionDecision("NOT_PROMOTED", reason, exp.experiment_id, metrics)
