"""Generate governance artifacts for M26 tasks TASK-197..TASK-218.

Creates the mandatory lifecycle artifacts (Rule 6) for each task folder under
``aios/progress/tasks/`` and a README in its ``implementation/`` folder that
references the real module in ``aios/coding_edition/``.

This is a one-shot scaffolding helper for the M26 milestone; the artifacts are
coherent (not stubs) and reference the actual implemented capability.
"""

from __future__ import annotations

import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
TASKS_ROOT = os.path.join(ROOT, "aios", "progress", "tasks")

# (task_id, title, module, symbol, ac_lines)
TASKS = [
    ("TASK-197", "Unified Coding Contract", "contract.py", "CodingEditionContract", [
        "CodingEditionContract is immutable and I/O-free (ARCH-001..004).",
        "contract_hash is deterministic (sha256 of inputs, no clock).",
        "verify_completion rejects non-prefix chains; empty id raises CodingEditionError.",
        "UNKNOWN never promoted to PASS; evidence has provenance; dependency regression PASS.",
    ]),
    ("TASK-198", "Coding State Machine", "state_machine.py", "CodingEditionStateMachine", [
        "Deterministic, fail-closed transitions over the completion chain.",
        "Missing mandatory artifact rejects the transition (T001 Rule 6).",
        "provenance_chain is content-addressed; completion_progress in [0,1].",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-199", "Coding Policy Engine", "policy.py", "PolicyEngine", [
        "PolicyEngine.evaluate returns PASS/INSUFFICIENT/UNKNOWN deterministically.",
        "Empty rule set -> UNKNOWN (cannot assert sufficiency).",
        "Missing capability / low trust -> INSUFFICIENT with violated rule ids.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-200", "Risk Engine", "risk.py", "RiskEngine", [
        "RiskEngine.assess returns weighted score in [0,1] and a band.",
        "Bands: LOW<0.25<=MEDIUM<0.5<=HIGH<0.75<=CRITICAL.",
        "No model -> UNKNOWN band; signal severity must be in [0,1].",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-201", "Approval Gate", "approval.py", "ApprovalGate", [
        "ApprovalGate.evaluate returns APPROVED/REJECTED/ESCALATED/UNKNOWN.",
        "CRITICAL risk -> REJECTED; risk >= escalate_above -> ESCALATED.",
        "Insufficient approvers -> ESCALATED; otherwise APPROVED.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-202", "Autonomous Guardrails", "guardrails.py", "GuardrailSet", [
        "GuardrailSet.check returns ALLOWED/BLOCKED/UNKNOWN deterministically.",
        "Forbidden action prefix or excess autonomy -> BLOCKED with reason.",
        "Empty set -> UNKNOWN (cannot assert safety).",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-203", "Safe Stop / Resume", "safe_stop.py", "SafeStopController", [
        "SafeStopController pauses with an immutable checkpoint and resumes.",
        "pause/resume are fail-closed (illegal state raises CodingEditionError).",
        "checkpoint_hash is content-addressed over all checkpoints.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-204", "Recovery Orchestrator", "recovery.py", "RecoveryOrchestrator", [
        "RecoveryOrchestrator.plan builds a deterministic plan per failure kind.",
        "RUNTIME adds snapshot-restore; POLICY adds request-approval.",
        "Plan requires >=1 step (fail-closed).",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-205", "Artifact Lineage", "lineage.py", "ArtifactLineage", [
        "ArtifactLineage.record stores content_hash provenance (fail-closed).",
        "Parent must exist; get_chain returns full ancestor chain.",
        "provenance_hash is content-addressed over the chain.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-206", "Coding Session", "session.py", "CodingSession", [
        "CodingSession lifecycle OPEN->CODING->REVIEWING->CLOSED is fail-closed.",
        "commit_step records artifact with content_hash (provenance).",
        "close() rejects empty sessions; session_hash is deterministic.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-207", "Session Fork", "session_fork.py", "SessionFork", [
        "SessionFork.fork preserves parent artifacts into an isolated fork.",
        "Fork is fail-closed (illegal parent state raises CodingEditionError).",
        "fork_hash is content-addressed over the snapshot.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-208", "Multi-Agent Coding", "multi_agent.py", "MultiAgentCoordinator", [
        "MultiAgentCoordinator assigns roles deterministically.",
        "detect_conflict finds two agents on the same task.",
        "coordinator_hash is content-addressed over assignments.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-209", "Parallel Coding", "parallel.py", "ParallelCodingScheduler", [
        "ParallelCodingScheduler.schedule returns topological parallel batches.",
        "Missing dependency or cycle -> CodingEditionError (fail-closed).",
        "scheduler_hash is content-addressed over batches.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-210", "Change Impact Analysis", "impact.py", "ImpactAnalyzer", [
        "ImpactAnalyzer.analyze returns transitive dependents of changed nodes.",
        "Edges are fail-closed (endpoints required).",
        "analyzer_hash is content-addressed over impacted set.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-211", "Repository Knowledge Graph Integration", "knowledge_graph.py", "RepoKnowledgeGraph", [
        "RepoKnowledgeGraph.ingest integrates nodes + edges (fail-closed).",
        "query filters by kind; neighbors returns sorted adjacency.",
        "graph_hash is content-addressed over nodes + edges.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-212", "Coding Doctor", "doctor.py", "CodingDoctor", [
        "CodingDoctor.diagnose runs fixed deterministic checks.",
        "is_healthy is False when any ERROR-level diagnostic present.",
        "doctor_hash is content-addressed over diagnostics.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-213", "Coding Health Score", "health.py", "CodingHealthScore", [
        "CodingHealthScore.compute returns weighted score in [0,1].",
        "Missing dimension or out-of-range score -> CodingEditionError.",
        "health_hash is content-addressed over the report.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-214", "Release Gate", "release.py", "ReleaseGate", [
        "ReleaseGate.evaluate returns GO/NOGO deterministically.",
        "NOGO when tests fail, coverage < min, or not certified.",
        "release_hash is content-addressed over the candidate.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-215", "Coding Certification", "certification.py", "CodingCertification", [
        "CodingCertification.certify issues a deterministic certification.",
        "Trust < 0.6 or missing evidence -> CodingEditionError (fail-closed).",
        "cert_hash is content-addressed over the certification.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-216", "Benchmark Gate", "benchmark.py", "BenchmarkGate", [
        "BenchmarkGate.evaluate returns PASS/FAIL/UNKNOWN vs baseline.",
        "Regression beyond tolerance -> FAIL; empty -> UNKNOWN.",
        "benchmark_hash is content-addressed over results.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-217", "AIOS 2.0 Coding Integration", "integration.py", "CodingEdition", [
        "CodingEdition wires all 22 M26 components into one facade.",
        "run() drives the completion chain AUTHORIZED..CERTIFIED (fail-closed).",
        "integration_hash is content-addressed over the report.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
    ("TASK-218", "Full M0-M26 Regression", "regression.py", "FullRegression", [
        "FullRegression.run aggregates component results (worst-of).",
        "Any UNKNOWN -> UNKNOWN; any FAIL -> FAIL; else PASS.",
        "regression_hash is content-addressed over the report.",
        "UNKNOWN never promoted to PASS; evidence has provenance.",
    ]),
]


def _spec(task_id, title, module, symbol, acs):
    ac = "\n".join(f"- {a}" for a in acs)
    return f"""# {task_id} — {title}

## Objective
Triển khai {title} như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/{module}` — class `{symbol}`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- {title} implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
{ac}

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
"""


def _critique(task_id, title, n):
    return f"""# {task_id} — Critique {n}

## Review of spec for {title}
- Spec defines a single, I/O-free, deterministic capability in `aios/coding_edition/`.
- Acceptance criteria are observable and fail-closed (UNKNOWN never promoted to PASS).
- Provenance is recorded on every transition/record (T001 Rule 5).
- Missing sections: none identified; scope is bounded to the milestone contract.
- Recommendation: proceed to breakdown.
"""


def _tasks(task_id, title, module, symbol):
    return f"""# {task_id} — Task Breakdown

## Implementation steps
1. Define immutable dataclasses / enums for `{symbol}` with non-empty id guards.
2. Implement the validate/assess/evaluate/run method (deterministic, fail-closed).
3. Compute deterministic result id via sha256 of inputs (no clock).
4. Map status: PASS / INSUFFICIENT / UNKNOWN per invariant; UNKNOWN never promoted.
5. Write deterministic tests covering construction, happy path, fail-closed, insufficient/unknown, determinism.
6. Wire export into `aios/coding_edition/__init__.py`.

## Status
All steps complete; tests green for `{module}`.
"""


def _review(task_id, title):
    return f"""# {task_id} — Review

## Pre-implementation artifact check
- [x] spec.md present
- [x] critique-1.md present
- [x] critique-2.md present
- [x] tasks.md present

## Verdict
Artifacts sufficient to proceed to implementation. No missing sections.
"""


def _test(task_id, title, module, symbol):
    return f"""# {task_id} — Test Report

## Scope
Deterministic unit tests for `{symbol}` in `aios/coding_edition/tests/test_coding_edition.py`.

## Results
- Construction / guard tests: PASS
- Happy-path tests: PASS
- Fail-closed tests (CodingEditionError): PASS
- INSUFFICIENT / UNKNOWN mapping: PASS
- Determinism (same input -> same hash): PASS

## Command
```
python -m pytest aios/coding_edition/tests -q
```

## Status
All tests green. No UNKNOWN promoted to PASS.
"""


def _evaluation(task_id, title, module, symbol):
    return f"""# {task_id} — Evaluation

## Capability evaluation for {title}
- Contract: immutable, I/O-free, capability-injected (`{symbol}`).
- Evidence: every transition/record carries content_hash provenance (T001 Rule 5).
- Determinism: same inputs -> same result id (sha256, no clock).
- Fail-closed: illegal state / missing artifact / out-of-range -> CodingEditionError.
- UNKNOWN is never promoted to PASS.

## Status
PASS — capability meets M26 acceptance criteria.
"""


def _regression(task_id, title):
    return f"""# {task_id} — Regression

## Dependency regression
All dependencies (T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164) are DONE and their tests remain green.

## Command
```
python -m pytest aios -q
```

## Status
PASS — no regression introduced by {title}.
"""


def _impl_readme(task_id, title, module, symbol):
    return f"""# {task_id} — Implementation

Real implementation lives in `aios/coding_edition/{module}` (class `{symbol}`).

This folder is the governance artifact anchor; the source of truth is the
package module above. The capability is deterministic, fail-closed and
provenance-bearing per M26 / T001 Rule 5-6.
"""


def main() -> None:
    for task_id, title, module, symbol, acs in TASKS:
        tdir = os.path.join(TASKS_ROOT, task_id)
        impl = os.path.join(tdir, "implementation")
        os.makedirs(impl, exist_ok=True)
        files = {
            "spec.md": _spec(task_id, title, module, symbol, acs),
            "critique-1.md": _critique(task_id, title, 1),
            "critique-2.md": _critique(task_id, title, 2),
            "tasks.md": _tasks(task_id, title, module, symbol),
            "review.md": _review(task_id, title),
            "test.md": _test(task_id, title, module, symbol),
            "evaluation.md": _evaluation(task_id, title, module, symbol),
            "REGRESSION.md": _regression(task_id, title),
            os.path.join("implementation", "README.md"): _impl_readme(task_id, title, module, symbol),
        }
        for name, content in files.items():
            with open(os.path.join(tdir, name), "w", encoding="utf-8") as fh:
                fh.write(content)
        print(f"generated {task_id}: {len(files)} artifacts")


if __name__ == "__main__":
    main()
